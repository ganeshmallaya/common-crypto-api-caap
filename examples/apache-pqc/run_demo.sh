#!/bin/sh
set -eu

repo_dir="$(CDPATH= cd -- "$(dirname "$0")/../.." && pwd)"
demo_dir="${CALI_APACHE_DEMO_DIR:-$(mktemp -d)}"
api_port="${CALI_APACHE_API_PORT:-18085}"
https_port="${CALI_APACHE_HTTPS_PORT:-18443}"
python_bin="${CALI_PYTHON:-$repo_dir/.venv/bin/python}"
httpd_bin="${CALI_HTTPD:-/usr/sbin/httpd}"
certificate_dir="$demo_dir/certificates"
runtime_dir="$demo_dir/apache"
selected_conf="$runtime_dir/selected-certificate.conf"
service_pid=""
apache_pid=""

cleanup() {
  if [ -n "$apache_pid" ]; then
    kill "$apache_pid" 2>/dev/null || true
    wait "$apache_pid" 2>/dev/null || true
  fi
  if [ -n "$service_pid" ]; then
    kill "$service_pid" 2>/dev/null || true
    wait "$service_pid" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

"$python_bin" - "$api_port" "$https_port" <<'PY'
import socket
import sys

for value in sys.argv[1:]:
    port = int(value)
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError as exc:
        raise SystemExit(f"loopback port {port} is unavailable: {exc}") from exc
    finally:
        sock.close()
PY

mkdir -p "$certificate_dir" "$runtime_dir/logs" "$runtime_dir/htdocs"
cp "$repo_dir/examples/apache-pqc/index.html" "$runtime_dir/htdocs/index.html"

openssl req -x509 -newkey ec -pkeyopt ec_paramgen_curve:P-256 -nodes \
  -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost' -days 1 \
  -keyout "$certificate_dir/ecdsa-key.pem" \
  -out "$certificate_dir/ecdsa-cert.pem" >/dev/null 2>&1

openssl req -x509 -newkey ML-DSA-65 -nodes \
  -subj '/CN=localhost' -addext 'subjectAltName=DNS:localhost' -days 1 \
  -keyout "$certificate_dir/mldsa65-key.pem" \
  -out "$certificate_dir/mldsa65-cert.pem" >/dev/null 2>&1

CALI_PORT="$api_port" \
CALI_POLICY_FILE="$repo_dir/examples/apache-pqc/policy-transition.json" \
CALI_CERTIFICATE_PROFILES='ecdsa-p256-sha256' \
  "$python_bin" -m cali_reference >"$runtime_dir/cali.log" 2>&1 &
service_pid=$!

i=0
until curl --fail --silent "http://127.0.0.1:$api_port/healthz" >/dev/null; do
  i=$((i + 1))
  if [ "$i" -gt 40 ]; then
    echo "CALI service did not start" >&2
    exit 1
  fi
  sleep 0.1
done

"$python_bin" "$repo_dir/examples/apache-pqc/select_certificate.py" \
  --api-url "http://127.0.0.1:$api_port" \
  --policy-version transition-1 \
  --certificate-dir "$certificate_dir" \
  --output "$selected_conf" >"$runtime_dir/transition-result.json"

cat >"$runtime_dir/httpd.conf" <<EOF
ServerRoot "$runtime_dir"
PidFile "$runtime_dir/httpd.pid"
Listen 127.0.0.1:$https_port
ServerName localhost
LoadModule mpm_prefork_module /usr/libexec/apache2/mod_mpm_prefork.so
LoadModule authz_core_module /usr/libexec/apache2/mod_authz_core.so
LoadModule authz_host_module /usr/libexec/apache2/mod_authz_host.so
LoadModule unixd_module /usr/libexec/apache2/mod_unixd.so
LoadModule socache_shmcb_module /usr/libexec/apache2/mod_socache_shmcb.so
LoadModule ssl_module /usr/libexec/apache2/mod_ssl.so
LoadModule log_config_module /usr/libexec/apache2/mod_log_config.so
ErrorLog "$runtime_dir/logs/error.log"
LogLevel warn
DocumentRoot "$runtime_dir/htdocs"
<Directory "$runtime_dir/htdocs">
  Require all granted
</Directory>
<VirtualHost 127.0.0.1:$https_port>
  ServerName localhost
  SSLEngine on
  Include "$selected_conf"
</VirtualHost>
EOF

"$httpd_bin" -t -f "$runtime_dir/httpd.conf"
"$httpd_bin" -f "$runtime_dir/httpd.conf" -DFOREGROUND &
apache_pid=$!
sleep 0.2
if ! kill -0 "$apache_pid" 2>/dev/null; then
  echo "Apache exited before the HTTPS check" >&2
  exit 1
fi

i=0
until curl --fail --silent --insecure \
  "https://localhost:$https_port/index.html" >"$runtime_dir/response.html"; do
  i=$((i + 1))
  if [ "$i" -gt 40 ]; then
    echo "Apache HTTPS application did not start" >&2
    exit 1
  fi
  sleep 0.1
done

before="$(shasum -a 256 "$selected_conf" | cut -d ' ' -f 1)"
kill "$service_pid"
wait "$service_pid" 2>/dev/null || true
service_pid=""

CALI_PORT="$api_port" \
CALI_POLICY_FILE="$repo_dir/examples/apache-pqc/policy-pqc-required.json" \
CALI_CERTIFICATE_PROFILES='ecdsa-p256-sha256' \
  "$python_bin" -m cali_reference >"$runtime_dir/cali-strict.log" 2>&1 &
service_pid=$!

i=0
until curl --fail --silent "http://127.0.0.1:$api_port/healthz" >/dev/null; do
  i=$((i + 1))
  if [ "$i" -gt 40 ]; then
    echo "CALI strict policy service did not start" >&2
    exit 1
  fi
  sleep 0.1
done

if "$python_bin" "$repo_dir/examples/apache-pqc/select_certificate.py" \
  --api-url "http://127.0.0.1:$api_port" \
  --policy-version pqc-required-1 \
  --certificate-dir "$certificate_dir" \
  --output "$selected_conf" >"$runtime_dir/strict-result.json" 2>"$runtime_dir/strict-error.log"; then
  echo "strict ML DSA policy unexpectedly succeeded" >&2
  exit 1
fi

after="$(shasum -a 256 "$selected_conf" | cut -d ' ' -f 1)"
if [ "$before" != "$after" ]; then
  echo "failed policy resolution changed the Apache certificate fragment" >&2
  exit 1
fi

curl --fail --silent --insecure \
  "https://localhost:$https_port/index.html" >/dev/null

echo "PASS: Apache served the application with the policy selected ECDSA certificate."
echo "PASS: Strict ML DSA policy failed because Apache did not declare ML DSA capability."
echo "PASS: The failed decision did not change the live Apache certificate configuration."
echo "Evidence directory: $runtime_dir"
