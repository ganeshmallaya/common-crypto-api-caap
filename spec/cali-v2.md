# Cryptographic Abstraction Layer Interface — candidate v2

Status: exploratory specification, version `2.0.0-draft`

The key words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** express candidate
requirements for experimentation. They do not imply standards-track status.

## 1. Scope

CALI defines the decisions and evidence that a Common Crypto API implementation
preserves between an authenticated consumer, policy authority, broker, and
provider. A transport binding may be HTTP, gRPC, an in-process interface, or a
local IPC mechanism, provided it preserves the same semantics.

CALI does not define cryptographic algorithms and does not replace PKCS#11,
KMIP, KMS APIs, JCA, OpenSSL, certificate authorities, ACME, CMP, EST, TLS, or
application protocol negotiation.

## 2. Stable concepts

- **Intent** names the outcome and context, such as `artifact-signing`.
- **Profile** fixes an operation shape, input interpretation, output encoding,
  and required security properties. Algorithms are substitutable only inside a
  profile whose wire and application semantics remain compatible.
- **Policy decision** identifies one active policy version, profile, algorithm,
  provider constraints, and key constraints.
- **Key reference** is opaque, tenant-scoped, and version-aware. It does not by
  itself prove custody or protection level.
- **Capability statement** is authenticated, freshness-bounded, and scoped. It
  reports possible behavior; it neither authorizes nor guarantees execution.
- **Evidence** records the decision and execution identifiers without payloads,
  credentials, private keys, or shared secrets.

## 3. Common execution request

Every policy-resolved cryptographic, key-lifecycle, or mutating operation request
MUST contain:

1. `apiVersion`;
2. a caller-generated `requestId` suitable for correlation and idempotency;
3. `intent` and `operation`;
4. operation-specific input with an explicit content encoding; and
5. `minimumConstraints`, even when empty.

`expectedPolicy` SHOULD pin a profile and version. Caller identity and tenant
MUST come from an authenticated channel or verified credential; a body field is
not sufficient. Implementations MUST set size limits and MUST reject unknown
critical fields or ambiguous input.

Health, capability discovery, and authorized metadata reads MAY use binding-
specific read requests without this body envelope. They still require the
authenticated scope, freshness, authorization-before-disclosure, size limits,
typed responses, and audit behavior defined by their operation profile.

## 4. Processing model

The broker MUST perform these steps in order:

1. authenticate the caller and establish tenant/workload context;
2. validate version, request ID, freshness, operation, intent, and encoding;
3. authorize the intent and operation before disclosing scoped capability;
4. resolve exactly one active policy decision and pin its version;
5. compare the decision with caller minimum constraints;
6. validate authenticated, fresh-enough provider capability;
7. validate key tenant, version, state, purpose, and provider binding;
8. dispatch exactly the resolved operation;
9. return typed result and evidence; and
10. emit a security event without secrets or unintended payload data.

Any failure stops processing. Implementations MUST NOT silently select a weaker
algorithm, different provider class, expired policy, older key version, or more
exportable key.

## 5. Common response and evidence

Policy-resolved execution success responses MUST correlate `requestId`, name the
operation, and include:

- policy profile ID and version;
- selected profile and algorithm identifier;
- provider reference and key reference/version when applicable;
- decision and execution timestamps; and
- an evidence ID suitable for authorized audit retrieval.

Provider identity MAY be redacted from an ordinary consumer response but MUST
remain available to authorized audit systems. Evidence does not prove hardware
assurance unless an assurance profile defines and verifies such evidence.

## 6. Failure model

| Category | Required meaning | Retry default |
| --- | --- | --- |
| `INVALID_REQUEST` | Unsafe, malformed, oversized, ambiguous, or unsupported request | no |
| `UNAUTHENTICATED` | No acceptable caller identity | after credential repair |
| `UNAUTHORIZED` | Caller lacks permission | no |
| `POLICY_NOT_FOUND` | No applicable decision | no |
| `POLICY_AMBIGUOUS` | Multiple incompatible decisions remain | no |
| `POLICY_INACTIVE` | Policy is early, expired, retired, or withdrawn | no |
| `CONSTRAINT_MISMATCH` | Decision violates a caller minimum | no |
| `CAPABILITY_MISMATCH` | No allowed provider can preserve the profile | after administrative change |
| `KEY_STATE_INVALID` | Key/version/purpose/state cannot perform the operation | no |
| `STATE_CONFLICT` | An optimistic resource version or lifecycle precondition changed | after state refresh |
| `IDEMPOTENCY_CONFLICT` | A replay key was reused with different canonical request content | no |
| `AUTHENTICATION_FAILED` | Well-formed protected data failed cryptographic authentication | profile-specific |
| `OUTPUT_RESTRICTED` | Policy or provider properties prohibit returning requested secret output | no |
| `RATE_LIMITED` | Authorized caller exceeded an enforced quota | when safe retry metadata permits |
| `PROVIDER_UNAVAILABLE` | Allowed provider is temporarily unavailable | operation-specific |
| `OPERATION_FAILED` | Provider attempted and failed without a safer category | operation-specific |
| `NOT_IMPLEMENTED` | Binding recognizes but does not implement the operation | no |

Errors MUST include a safe human-readable message and `retryable`. They MUST NOT
leak key existence across authorization boundaries or expose provider secrets.

## 7. Operation families

| Family | Operations | Candidate contract status |
| --- | --- | --- |
| Discovery | capabilities, profiles, provider classes | specified; capabilities implemented |
| Policy | resolve/dry-run, lifecycle, hierarchical evaluation | resolve implemented; lifecycle planned |
| Keys | create, read, list, rotate, transform, migrate, state, import/export, destroy | create/read implemented; remainder specified/planned |
| Signature | sign, verify, digest-sign, digest-verify | message sign/verify implemented |
| Encryption | authenticated encrypt/decrypt; bounded asymmetric forms | specified/planned |
| MAC | generate/verify | specified/planned |
| Digest/XOF/random | one-shot operations | specified/planned |
| Establishment | wrap/unwrap, derive, agree, encapsulate/decapsulate | specified/planned |
| Streaming | init/update/final with server-generated operation ID | planned after one-shot conformance |

All operation-specific documents MUST define purpose, authorization, exact input
interpretation, limits, idempotency/retry behavior, key states, output encoding,
evidence, and error refinements.

The candidate cross-family shapes and invariants are defined in
[`operation-contracts.md`](operation-contracts.md). That document distinguishes
implemented, specified, and reserved operations; specification does not imply
reference-service availability.

## 8. Artifact-signing profile v0

Profile identifier: `artifact-signing-v0` (experimental).

- Input is non-empty arbitrary bytes supplied as canonical unpadded base64.
- The implementation signs the decoded message bytes exactly once; it MUST NOT
  guess whether the bytes are a message or digest.
- The implemented algorithm is
  `http://www.w3.org/2021/04/xmldsig-more#eddsa-ed25519`, the Ed25519 identifier
  registered by RFC 9231, using a software provider.
- Signature and public key are canonical unpadded base64 in the HTTP binding.
- Key purpose is `sign`; creation returns public material and an opaque private
  key reference.
- Sign requires the active key version. Verify MAY name an earlier retained
  version when lifecycle support is added.
- Empty messages, malformed base64, unknown key references, non-signing keys,
  inactive policy, and constraint mismatch fail explicitly.

This profile demonstrates processing semantics. It does not yet constitute a
portable conformance profile because canonical vectors and a second
implementation are outstanding.

## 9. Lifecycle invariants

Rotation creates a new key version. Transformation across algorithm families
creates successor key material; it does not reinterpret or convert old bytes.
Migration MUST name a custody strategy and preserve old-version handling.
Destructive lifecycle actions require distinct authorization and evidence.

## 10. Versioning

Specification, binding, schema, profile, policy, template, and algorithm catalog
versions are independent. Additive syntax is not automatically semantically
compatible. A promoted version requires compatibility tests and a documented
change classification.

## 11. Conformance

An implementation MUST identify the exact profiles and binding versions it
implements. Repository tests currently establish only behavior of the included
reference slice. CALI conformance is undefined until the black-box runner,
positive and negative vectors, and conformance policy are published.
