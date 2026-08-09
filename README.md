# Crypto Agility Algorithm Protocol (CAAP)

CAAP is an independent, vendor-neutral research project for a policy-controlled
abstraction between applications and cryptographic implementations. The
research specification defines the control and protocol boundaries. The
**Common Crypto API** is the consumer-facing interface described by CAAP.

This repository is an early research workspace. It is not a standard, is not
affiliated with a standards body, and does not claim a working implementation,
interoperability, certification, or product support.

## Canonical naming

| Name | Meaning |
| --- | --- |
| **Crypto Agility Algorithm Protocol (CAAP)** | The research specification and policy model |
| **Common Crypto API** | The stable consumer interface defined by CAAP |
| `common-crypto-api-caap` | The repository name |

Use **CAAP** only as the abbreviation for **Crypto Agility Algorithm Protocol**.

## Research question

Can applications express a cryptographic intent without binding themselves to
one algorithm, provider, certificate authority, hardware security module
(HSM), key management service (KMS), or key store, while retaining explicit
policy, authorization, audit, and downgrade controls?

CAAP explores that question through two contracts:

1. A Common Crypto API used by consumers to request operations by intent.
2. A provider interface used by adapters for software libraries, HSMs, KMSs,
   and key stores.

Certificate authorities integrate at the workflow boundary. CAAP can provide
the key and signing operations used by certificate workflows, but it does not
replace enrollment, issuance, revocation, or certificate-management protocols.

## Repository map

- [`docs/problem-statement.md`](docs/problem-statement.md) explains the problem
  and research goals.
- [`docs/terminology.md`](docs/terminology.md) fixes the working vocabulary.
- [`docs/architecture.md`](docs/architecture.md) describes the component and
  trust boundaries.
- [`docs/protocol.md`](docs/protocol.md) defines the candidate interaction
  model and operation boundaries.
- [`docs/threat-model.md`](docs/threat-model.md) identifies assets, actors,
  trust boundaries, and threats.
- [`docs/security-considerations.md`](docs/security-considerations.md) records
  security requirements and unresolved decisions.
- [`docs/framework-v1.md`](docs/framework-v1.md) is the consolidated research
  framework for the vendor-neutral cryptographic abstraction layer.
- [`docs/control-plane-and-kmip.md`](docs/control-plane-and-kmip.md) separates
  policy authority from broker enforcement and maps KMIP as a provider path.
- [`docs/draft-alignment.md`](docs/draft-alignment.md) reviews the historical
  first draft against the proposed revision 02 architecture.
- [`docs/publication-workflow.md`](docs/publication-workflow.md) defines the
  versioned, copy-based website synchronization process.
- [`schemas/`](schemas/) contains experimental JSON Schemas. They are research
  artifacts, not a normative wire format.
- [`examples/`](examples/) contains non-production examples using reserved
  identifiers.
- [`public-export/`](public-export/) is the only website publication boundary.

## Source material already present

The files below predate this repository structure and remain useful research
inputs, but they are not authoritative CAAP documents:

- `common-crypto-api-spec-draft-v0.1.md`
- `common-crypto-api-reference-architecture.html`
- `common-crypto-api-reference-architecture_1.html` (byte-identical duplicate)

They contain earlier naming and design assumptions. New work should cite or
promote individual ideas only after review against the documents in `docs/`.

## Public website boundary

The research repository is authoritative. The personal website must not fetch
this repository at runtime and must not include it as a Git submodule. Reviewed
content is copied from `public-export/` at a pinned source commit. A draft or a
manifest without a source commit is not eligible for synchronization.

The initial export is intentionally limited to a “Content coming soon” page.

## Local validation

The contract checks use only the Python standard library:

```sh
python3 -m unittest discover -s tests -v
```

## Working rules

See [`AGENTS.md`](AGENTS.md). Do not push, publish, claim standards status, or
promote a draft public export without explicit approval.
