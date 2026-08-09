# Reference service

This is a deliberately small, non-production implementation of the
`artifact-signing-v0` profile. It exists to make policy resolution, provider
dispatch, evidence, and failure semantics executable. It is not an SDK and is
not a security-reviewed signing service.

## Run

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m cali_reference
```

Defaults: `127.0.0.1:8080`, in-memory keys, software provider, and development
authentication disabled. Set `CALI_AUTH_TOKEN` to require
`Authorization: Bearer <token>`. Never expose the development server publicly.

The process deliberately has no persistent private-key storage, TLS termination,
rate limiting, tenant directory, external policy authority, or hardware-backed
provider. It also has no idempotency-result store: repeating a mutating request
may repeat the operation. Restarting destroys all keys.

## Implemented flow

1. Validate the request envelope and operation.
2. Establish a development tenant from `X-CALI-Tenant` (default `local-dev`).
3. Resolve and pin the built-in active policy.
4. Compare caller minimum constraints.
5. match the software provider's scoped capability;
6. create or use an opaque tenant-bound key reference;
7. execute Ed25519 signing/verification; and
8. return a non-secret evidence record.

The header-based tenant mechanism is a test harness only, not authentication.
Capability discovery returns the development tenant scope, provider identity,
key-protection class, generation time, and a five-minute validity bound. It is
still not authorization or a guarantee that a later request will succeed.
