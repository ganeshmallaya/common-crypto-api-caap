# Apache TLS migration example

This runnable example shows how an engineer can place certificate selection
behind CALI without giving the application or deployment script permission to
choose any certificate it finds on disk.

The demonstration performs two policy phases.

1. The transition policy prefers ML DSA 65 and explicitly permits ECDSA P 256.
   The local Apache capability declaration contains only ECDSA, so the broker
   selects the approved ECDSA certificate and returns decision evidence.
2. The strict policy permits only ML DSA 65. Apache still declares only ECDSA.
   The broker returns `CAPABILITY_MISMATCH`. The deployment helper does not
   rewrite the Apache fragment and the running HTTPS application remains
   available with its last approved certificate.

This is a real Apache HTTPS run and a real policy failure test. It is not an ML
DSA TLS interoperability claim. The Homebrew OpenSSL command creates an ML DSA
certificate for inspection, but macOS Apache links to the operating system TLS
library and does not declare ML DSA capability in this example.

## Run

From the repository root:

```sh
.venv/bin/python -m pip install -e '.[dev]'
examples/apache-pqc/run_demo.sh
```

Expected output:

```text
PASS: Apache served the application with the policy selected ECDSA certificate.
PASS: Strict ML DSA policy failed because Apache did not declare ML DSA capability.
PASS: The failed decision did not change the live Apache certificate configuration.
```

The command prints a temporary evidence directory. Inspect these files:

* `transition-result.json` contains the pinned policy, selected profile and
  evidence identifier.
* `selected-certificate.conf` is the fragment Apache consumed.
* `strict-error.log` contains the expected capability failure.
* `response.html` proves that the Apache application answered over HTTPS.

## Where policy is defined

[`policy-transition.json`](policy-transition.json) and
[`policy-pqc-required.json`](policy-pqc-required.json) are the policy authority
inputs. Set `CALI_POLICY_FILE` when the broker starts. The broker validates the
policy status and effective time before listening for requests.

`CALI_CERTIFICATE_PROFILES` is the deployment capability declaration. It is not
policy. Policy says what may be used. Capability says what this Apache instance
can execute. The broker requires both to match.
