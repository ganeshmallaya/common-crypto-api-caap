# Roadmap

Status labels are evidence-based: **implemented** has executable tests in this
repository; **specified** has candidate contract text but no complete backend;
**planned** is design intent only.

## Milestone 0 — repository foundation (implemented)

- Canonical CAAP/Common Crypto API naming and trust boundaries.
- Candidate HTTP/OpenAPI binding and JSON Schemas.
- Minimal in-memory broker, software provider, pinned policy resolution, and
  explicit error model.
- Repo-hosted static research page and CI/Pages workflows.

## Milestone 1 — artifact-signing profile (implemented research slice)

- `CreateKey`, `Sign`, `Verify`, `ResolvePolicy`, and scoped capabilities.
- Ed25519 software provider, opaque key references, response evidence, and
  positive/negative tests.
- Remaining exit criteria: transport-independent test vectors, canonical byte
  encoding, persistent idempotency behavior, independent black-box runner, and
  a second implementation.

## Milestone 2 — primitive coverage (specified, implementation planned)

In order: digest and random; MAC; authenticated encrypt/decrypt; key derivation;
key agreement; encapsulation/decapsulation; key wrap/unwrap; then carefully
bounded streaming forms. Each primitive requires typed inputs, output encoding,
retry/idempotency rules, negative vectors, and provider-equivalence tests.

Algorithm coverage expands only inside a stable operation profile. Combined or
hybrid cryptography requires a separately reviewed construction; concatenating
two outputs is not a CAAP construction.

## Milestone 3 — lifecycle and migration (specified, implementation planned)

- Rotation creates a new version under the same logical key reference.
- Algorithm transformation creates successor key material and retains versioned
  verification/decryption continuity; it is not mathematical key conversion.
- Provider migration uses an explicit strategy: provider switch,
  extract/import, wrapped transfer, rekey/archive, or rekey/destroy.
- Import, export, backup, restore, suspension, revocation, destruction, and
  cryptoperiod state have independent permissions and audit events.

## Milestone 4 — provider ecosystem (planned)

- OpenSSL software adapter.
- PKCS#11 adapter with mechanism, session, object, and error mapping.
- KMIP adapter with Unique Identifier, state, usage-mask, extractability, and
  native result status/reason preservation.
- Cloud KMS adapter contract.
- JCA provider bridge feasibility study.

A software adapter plus one materially different custody backend is required
before interoperability claims.

## Milestone 5 — policy and knowledge base (partly implemented)

- Experimental algorithm-profile schema and source-backed artifact-signing
  record: **implemented**.
- Richer versioned template catalog and reviewed security properties:
  **planned**.
- Hierarchical organizational and regulatory profiles.
- Signed policy distribution, rollback resistance, cache expiry, staged
  activation, emergency withdrawal, and conflict resolution.
- Declarative reconciliation for key evolution with approval gates, dry-run,
  blast-radius reporting, and reversible rollout where feasible.

## Milestone 6 — bindings, state, and deployment (partly implemented)

- REST/HTTP reference binding: **implemented**.
- gRPC plus generated gateway: **planned** after contract stabilization.
- Encrypted persistent metadata and key-reference mapping: **planned**; raw
  private keys remain provider-owned.
- Local library, remote service, and hybrid control-plane deployments:
  **specified**, with only the remote development service implemented.
- Docker and Kubernetes packaging: **planned after the API process model and
  health/readiness contract stabilize**.

## Milestone 7 — conformance and governance (partly implemented)

- Versioned positive and negative vectors.
- Implementation-independent black-box test runner.
- Contribution guide and private security-reporting policy: **implemented**.
- Compatibility policy, registries, changelog, IPR/patent policy, and release
  process: **planned**.
- At least two independent implementations and recorded cross-provider results.
- Only then evaluate an appropriate open-standards venue.

## Coverage commitment

The roadmap covers functions, algorithm expansion, PKCS#11/OpenSSL/KMS/JCA
providers, the knowledge base, a gRPC Gateway, encrypted persistence,
hierarchical and regulatory policy, local/remote/hybrid deployment, declarative
evolution, and container/Kubernetes packaging. Each area remains subject to
explicit conformance, evidence, policy-provenance, failure, and independent-
implementation gates.
