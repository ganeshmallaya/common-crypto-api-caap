# Cryptographic Abstraction Layer Interface (CALI)

CALI is proprietary, vendor-neutral research by **Ganesh Mallaya** for a
policy-controlled cryptographic abstraction layer. The **Common Crypto API** is
the consumer interface defined by CALI; `cali-crypto-interface` is this
repository.

Research site: <https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/>

The project asks a bounded question: can an application request a cryptographic
outcome without hard-coding an algorithm or provider, while the system preserves
authorization, pinned policy, explicit failures, key custody and usable audit
evidence?

> **Research status:** exploratory v2.0 and not production ready. This is not a standard,
> certification, security assurance or interoperability claim. The schemas and
> HTTP binding are research contracts until the conformance milestones in the
> roadmap are met.

## Start here

| Need | Document or code |
| --- | --- |
| Understand the model | [`spec/cali-v2.md`](spec/cali-v2.md) |
| Review every operation family | [`spec/operation-contracts.md`](spec/operation-contracts.md) |
| Consume the operation catalog | [`api/operation-registry.json`](api/operation-registry.json) |
| Inspect the v2 classical-to-PQC profile | [`api/profiles/pqc-signing-v2.profile.json`](api/profiles/pqc-signing-v2.profile.json) |
| Use the HTTP contract | [`api/openapi/cali-v2.openapi.json`](api/openapi/cali-v2.openapi.json) |
| Run the reference service | [`reference/README.md`](reference/README.md) |
| Run the Apache migration example | [`examples/apache-pqc/README.md`](examples/apache-pqc/README.md) |
| See supported versus planned operations | [`ROADMAP.md`](ROADMAP.md) |
| Review alignment to NIST crypto-agility guidance | [`docs/nist-cswp-39-alignment.md`](docs/nist-cswp-39-alignment.md) |
| Understand threats and non-goals | [`docs/security-considerations.md`](docs/security-considerations.md) |
| Read the native research site | [ganeshmallaya.com research](https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/) |

## The two contracts

```text
authenticated consumer
        | Common Crypto API: intent + operation + constraints
        v
     CALI broker <---- pinned decision ---- policy authority
        |
        | provider contract: resolved operation + opaque key reference
        v
 provider adapter ---- software / PKCS#11 / KMIP / cloud KMS / JCA
```

The broker enforces a policy decision; it does not silently choose a fallback.
Capability discovery is scoped and is not authorization. Private keys remain
behind opaque references by default. Existing cryptographic standards and
provider APIs remain below CALI rather than being replaced by it.

## What runs today

The v2 contract and examples concentrate on RSA-PSS, ECDSA P-256, ML-DSA-65,
and an explicit ECC-to-ML-DSA migration. The Python reference service still
implements one deliberately small Ed25519 vertical slice:

- scoped capability discovery;
- pinned policy resolution;
- Ed25519 key generation using an in-memory software provider;
- artifact signing and verification;
- stable CALI error categories and evidence metadata;
- optional development bearer authentication, off by default; and
- HTTP/JSON endpoints described by the checked-in OpenAPI document.

Everything else is maturity-labelled in [`ROADMAP.md`](ROADMAP.md). Unsupported
behavior must fail explicitly; it must never fall back to another algorithm,
provider, policy or key-protection level.

The service also implements policy driven certificate selection for the Apache
migration demonstration. Transition policy selects an approved ECDSA
certificate when Apache declares only ECDSA capability. Strict ML DSA policy
fails with `CAPABILITY_MISMATCH` and leaves the live Apache certificate fragment
unchanged. This tests migration control and failure behavior. It does not claim
an ML DSA TLS handshake.

## Quick start

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m cali_reference
```

In another terminal:

```sh
curl http://127.0.0.1:8080/v2/capabilities
```

The runnable end-to-end example is in [`examples/quickstart.sh`](examples/quickstart.sh).

The live Apache policy example is:

```sh
examples/apache-pqc/run_demo.sh
```

## Validation

```sh
python3 -m unittest discover -s tests -v
```

## Repository layout

```text
api/          research HTTP and OpenAPI binding
docs/         architecture, analysis, security and governance
examples/     non-production requests and a runnable flow
reference/    minimal broker and software provider
schemas/      experimental JSON Schema contracts
spec/         CALI specification
tests/        contract and reference-implementation tests
```

The repository intentionally contains no SDK. Generated or hand-written clients
should be tested against the API contract and conformance vectors rather than
treated as the specification.

## Ownership and public-repository decisions

Copyright © 2026 Ganesh Mallaya. All rights reserved. This is proprietary
research. The repository may be made publicly viewable for research review,
but no copyright license is granted until
the maintainer deliberately adds one. See [`NOTICE.md`](NOTICE.md).

Research feedback and private vulnerability reporting are described in
[`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SECURITY.md`](SECURITY.md). Approve
the first release status before public release. CALI is informed by
[NIST CSWP 39upd1](https://doi.org/10.6028/NIST.CSWP.39-upd1), but is not a NIST
publication, standard, implementation, endorsement or conformance claim. CALI
is developed independently and has no affiliation with, sponsorship by,
compatibility claim to or endorsement from any existing implementation.
