# Crypto Agility Algorithm Protocol (CAAP)

CAAP is proprietary, vendor-neutral research by **Ganesh Mallaya** for a
policy-controlled cryptographic abstraction layer. The **Common Crypto API** is
the consumer interface defined by CAAP; `common-crypto-api-caap` is this
repository.

Research site: <https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/>

The project asks a bounded question: can an application request a cryptographic
outcome without hard-coding an algorithm or provider, while the system preserves
authorization, pinned policy, explicit failures, key custody, and usable audit
evidence?

> **Research status:** pre-1.0 and not production-ready. This is not a standard,
> certification, security assurance, or interoperability claim. The schemas and
> HTTP binding are candidate contracts until the conformance milestones in the
> roadmap are met.

## Start here

| Need | Document or code |
| --- | --- |
| Understand the model | [`spec/caap-v1.md`](spec/caap-v1.md) |
| Review every operation family | [`spec/operation-contracts.md`](spec/operation-contracts.md) |
| Consume the operation catalog | [`api/operation-registry.json`](api/operation-registry.json) |
| Inspect the implemented profile record | [`api/profiles/artifact-signing-v0.profile.json`](api/profiles/artifact-signing-v0.profile.json) |
| Use the HTTP contract | [`api/openapi/caap-v1.openapi.json`](api/openapi/caap-v1.openapi.json) |
| Run the reference service | [`reference/README.md`](reference/README.md) |
| See supported versus planned operations | [`ROADMAP.md`](ROADMAP.md) |
| Review alignment to NIST crypto-agility guidance | [`docs/nist-cswp-39-alignment.md`](docs/nist-cswp-39-alignment.md) |
| Understand threats and non-goals | [`docs/security-considerations.md`](docs/security-considerations.md) |
| Host the research page | [`site/README.md`](site/README.md) |

## The two contracts

```text
authenticated consumer
        | Common Crypto API: intent + operation + constraints
        v
     CAAP broker <---- pinned decision ---- policy authority
        |
        | provider contract: resolved operation + opaque key reference
        v
 provider adapter ---- software / PKCS#11 / KMIP / cloud KMS / JCA
```

The broker enforces a policy decision; it does not silently choose a fallback.
Capability discovery is scoped and is not authorization. Private keys remain
behind opaque references by default. Existing cryptographic standards and
provider APIs remain below CAAP rather than being replaced by it.

## What runs today

The Python reference service implements one deliberately small vertical slice:

- scoped capability discovery;
- pinned policy resolution;
- Ed25519 key generation using an in-memory software provider;
- artifact signing and verification;
- stable CAAP error categories and evidence metadata;
- optional development bearer authentication, off by default; and
- HTTP/JSON endpoints described by the checked-in OpenAPI document.

Everything else is maturity-labelled in [`ROADMAP.md`](ROADMAP.md). Unsupported
behavior must fail explicitly; it must never fall back to another algorithm,
provider, policy, or key-protection level.

## Quick start

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e '.[dev]'
python -m caap_reference
```

In another terminal:

```sh
curl http://127.0.0.1:8080/v1/capabilities
```

The runnable end-to-end example is in [`examples/quickstart.sh`](examples/quickstart.sh).

## Validation

```sh
python3 -m unittest discover -s tests -v
```

## Repository layout

```text
api/          candidate HTTP/OpenAPI binding
docs/         architecture, analysis, security, and governance
examples/     non-production requests and a runnable flow
integration/  reviewed cross-repository configuration fragments
reference/    minimal broker and software provider
schemas/      experimental JSON Schema contracts
site/         static research site, deployable from this repository
spec/         CAAP specification
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
the first release status before public release. CAAP is informed by
[NIST CSWP 39upd1](https://doi.org/10.6028/NIST.CSWP.39-upd1), but is not a NIST
publication, standard, implementation, endorsement, or conformance claim. CAAP
is developed independently and has no affiliation with, sponsorship by,
compatibility claim to, or endorsement from any existing implementation.
