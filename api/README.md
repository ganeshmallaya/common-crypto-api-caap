# API bindings

CAAP separates transport-independent semantics from concrete bindings:

- [`../spec/caap-v1.md`](../spec/caap-v1.md) defines the core processing,
  trust, failure, evidence, and versioning contract.
- [`../spec/operation-contracts.md`](../spec/operation-contracts.md) defines the
  candidate shapes and invariants across every requested operation family.
- [`operation-registry.json`](operation-registry.json) provides a
  machine-readable operation, maturity, state, key-material, and retry index.
- [`profiles/artifact-signing-v0.profile.json`](profiles/artifact-signing-v0.profile.json)
  is the source-level algorithm-profile record for the implemented slice.
- [`openapi/caap-v1.openapi.json`](openapi/caap-v1.openapi.json) describes only
  the HTTP endpoints implemented by the current reference slice.

The OpenAPI document deliberately does not publish unimplemented endpoints as
if they were available. Each operation carries an `x-caap-maturity` marker and,
where applicable, an `x-caap-profile` marker. A later binding may add specified
operations only when its request/response schemas and reference behavior agree
with the transport-independent operation contract.

The optional bearer scheme and `X-CAAP-Tenant` header are development harness
features, not a production identity model. A production binding must derive
caller and tenant context from authenticated credentials and channel binding.
