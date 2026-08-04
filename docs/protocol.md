# Protocol boundaries

Status: experimental interaction model; not a normative wire protocol

## Scope

This document identifies the information and sequencing a future CAAP binding
needs to preserve. It does not select gRPC, OpenAPI, CDDL, a native ABI, or any
other binding.

The experimental envelopes in [`schemas/protocol-envelope.schema.json`](../schemas/protocol-envelope.schema.json)
exist to test the model. They are not an interoperability claim.

## Common request context

Every request needs enough information to support authentication, replay
handling, policy pinning, and audit:

- API version
- unique request identifier
- operation
- intent
- authenticated caller context (normally derived from the channel, not trusted
  merely because it appears in a body)
- caller minimum constraints
- optional expected policy profile and version
- operation-specific input

Secrets and raw private key material are not common request fields.

## Candidate operation groups

### Discovery and evaluation

- `GetCapabilities`: obtain a scoped capability descriptor.
- `ResolvePolicy`: dry-run a decision without performing a cryptographic
  operation.

### Key lifecycle

- `GenerateKeyPair`: create a key under resolved policy and return an opaque key
  reference plus non-secret metadata.
- Key import, export, rotation, and destruction are intentionally unresolved.
  They require separate authorization and lifecycle semantics.

### Signature

- `Sign`: sign an explicitly typed input using a key reference.
- `Verify`: verify using a key reference or explicitly typed public material.

Whether a binding accepts a message, digest, or structured protocol object must
be explicit. An implementation must not guess or silently hash twice.

### Key establishment

- `Encapsulate`: return a ciphertext and a protected representation of the
  derived secret appropriate to the deployment.
- `Decapsulate`: consume a key reference and ciphertext and return a protected
  representation of the secret.

Returning raw shared secrets across a network boundary is not assumed. A future
binding needs an explicit secret-delivery model.

## Resolution and execution sequence

1. Authenticate the caller and establish tenant/workload context.
2. Validate request version, identifier, freshness, intent, and operation.
3. Authorize the intent and operation before resolving a provider.
4. Resolve against a pinned, active policy profile.
5. Compare the decision with caller minimum constraints.
6. Obtain or use fresh-enough authenticated provider capability information.
7. Validate key-reference state and compatibility when a key is involved.
8. Dispatch exactly the resolved operation or reject it.
9. Return the decision metadata needed for audit, without returning secrets.
10. Record a tamper-evident security event appropriate to the deployment.

## Response metadata

A successful response should identify:

- request identifier
- API version
- operation
- policy profile and version
- selected algorithm namespace and identifier
- provider reference suitable for audit but not containing credentials
- key reference when applicable
- decision and operation timestamps

Whether provider identity is visible to the consumer is a policy and privacy
question. It must remain available to authorized audit systems.

## Failure categories

| Category | Meaning |
| --- | --- |
| `INVALID_REQUEST` | The request cannot be interpreted safely. |
| `UNAUTHORIZED` | The caller cannot perform the intent or operation. |
| `POLICY_NOT_FOUND` | No applicable policy profile exists. |
| `POLICY_AMBIGUOUS` | More than one incompatible decision remains. |
| `POLICY_INACTIVE` | The selected profile is not yet effective, expired, withdrawn, or otherwise inactive. |
| `CONSTRAINT_MISMATCH` | The decision cannot meet a caller or policy minimum. |
| `CAPABILITY_MISMATCH` | No allowed provider capability matches the decision. |
| `KEY_STATE_INVALID` | A key is absent, revoked, expired, destroyed, or otherwise unusable. |
| `PROVIDER_UNAVAILABLE` | The selected provider cannot currently execute the operation. |
| `OPERATION_FAILED` | The provider attempted the operation but it failed without a safer specific category. |

Retries must be defined per category and operation. Key generation and signing
are not automatically safe to retry without idempotency semantics.

## Versioning

API, schema, policy-profile, and algorithm-identifier versions are independent.
Each must be explicit. Additive syntax is not automatically a compatible
semantic change; compatibility tests are required before a version is promoted.

## Open protocol decisions

- Normative interface definition language and transport binding
- Request authentication, channel binding, and workload identity
- Policy signing, distribution, cache expiry, and rollback prevention
- Idempotency and retry rules per operation
- Public-key and signature encoding
- Secret-delivery semantics for KEM and derivation operations
- Combined-algorithm composition and encoding
- Provider-attestation vocabulary and evidence verification
- Audit-event format and privacy controls
