"""HTTP/JSON binding for the CALI research broker."""

from __future__ import annotations

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote, urlparse

from .broker import Broker, CaliError
from .policy import PolicyLoadError, load_policy


MAX_BODY = 1024 * 1024


def make_handler(broker: Broker, auth_token: str | None = None):
    class Handler(BaseHTTPRequestHandler):
        server_version = "CALIReference/2.0"

        def do_GET(self) -> None:  # noqa: N802
            try:
                self._authenticate()
                path = urlparse(self.path).path
                if path == "/healthz":
                    self._send(200, {"status": "ok"})
                elif path == "/v2/capabilities":
                    self._send(200, broker.capabilities(self._tenant()))
                elif path.startswith("/v2/keys/"):
                    self._send(200, broker.read_key(unquote(path.removeprefix("/v2/keys/")), self._tenant()))
                else:
                    self._send(404, CaliError("INVALID_REQUEST", "route not found", status=404).response())
            except CaliError as exc:
                self._send(exc.status, exc.response())

        def do_POST(self) -> None:  # noqa: N802
            try:
                self._authenticate()
                route_operation = {"/v2/policies:resolve": "ResolvePolicy", "/v2/keys": "CreateKey", "/v2/sign": "Sign", "/v2/verify": "Verify", "/v2/certificates:select": "SelectCertificate"}.get(urlparse(self.path).path)
                if route_operation is None:
                    raise CaliError("INVALID_REQUEST", "route not found", status=404)
                request = self._read_json()
                if request.get("operation") != route_operation:
                    raise CaliError("INVALID_REQUEST", "operation does not match route")
                status, response = broker.execute(request, self._tenant())
                self._send(status, response)
            except CaliError as exc:
                self._send(exc.status, exc.response())

        def _authenticate(self) -> None:
            if auth_token and self.headers.get("Authorization") != f"Bearer {auth_token}":
                raise CaliError("UNAUTHENTICATED", "valid bearer credential required", status=401)

        def _tenant(self) -> str:
            value = self.headers.get("X-CALI-Tenant", "local-dev")
            if not value or len(value) > 128 or not all(c.isalnum() or c in "._-" for c in value):
                raise CaliError("INVALID_REQUEST", "invalid development tenant")
            return value

        def _read_json(self):
            content_type = self.headers.get("Content-Type", "").split(";", 1)[0].strip()
            if content_type != "application/json":
                raise CaliError("INVALID_REQUEST", "Content-Type must be application/json", status=415)
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError as exc:
                raise CaliError("INVALID_REQUEST", "invalid Content-Length") from exc
            if length <= 0 or length > MAX_BODY:
                raise CaliError("INVALID_REQUEST", "request body size is invalid", status=413)
            try:
                return json.loads(self.rfile.read(length))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                raise CaliError("INVALID_REQUEST", "request body is not valid JSON") from exc

        def _send(self, status: int, value) -> None:
            body = json.dumps(value, separators=(",", ":")).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, format: str, *args) -> None:
            print(f"{self.address_string()} {format % args}")

    return Handler


def main() -> None:
    host = os.getenv("CALI_HOST", "127.0.0.1")
    port = int(os.getenv("CALI_PORT", "8080"))
    auth_token = os.getenv("CALI_AUTH_TOKEN") or None
    policy_path = os.getenv("CALI_POLICY_FILE")
    try:
        certificate_policy = load_policy(policy_path) if policy_path else None
    except PolicyLoadError as exc:
        raise SystemExit(f"CALI policy error: {exc}") from exc
    profiles = {
        item.strip()
        for item in os.getenv("CALI_CERTIFICATE_PROFILES", "ecdsa-p256-sha256").split(",")
        if item.strip()
    }
    server = ThreadingHTTPServer(
        (host, port),
        make_handler(Broker(certificate_policy, profiles), auth_token),
    )
    print(f"CALI research server listening on http://{host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
