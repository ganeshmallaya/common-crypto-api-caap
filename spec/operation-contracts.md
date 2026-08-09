# CAAP operation contracts — candidate 0.2.0

Status: exploratory companion to [`caap-v1.md`](caap-v1.md).

This document defines the operation shapes that a Common Crypto API binding
must preserve. It is intentionally algorithm-independent. An algorithm profile
may narrow a shape, but it must not silently change the meaning of an input or
output.

The key words **MUST**, **MUST NOT**, **SHOULD**, and **MAY** express candidate
research requirements. They do not imply standards-track or conformance status.

## 1. Maturity vocabulary

| Label | Meaning |
| --- | --- |
| `implemented` | Executable in the included reference service and covered by repository tests. |
| `specified` | Operation semantics are defined here, but the included reference service does not implement them. |
| `reserved` | Name is reserved for investigation; no portable contract is claimed. |

An implementation MUST advertise only the operations and profiles it actually
implements. Recognition of an operation name is not capability. The reference
service MUST return `NOT_IMPLEMENTED` for a recognized but unavailable
operation and MUST NOT route it to a similar primitive.

## 2. Common operation envelope

Every policy-resolved execution operation uses the common request fields in the
core specification:

```text
apiVersion + requestId + intent + operation
expectedPolicy? + minimumConstraints + input
```

Authenticated transport context supplies the caller, tenant, workload, channel
binding, and freshness evidence. A binding that carries any of those values in
the body MUST treat them as assertions to verify, never as trusted context by
themselves.

Health, capability discovery, and authorized metadata reads may use typed GET
requests without an execution body. Their path/query/header fields remain part
of the binding contract and must not bypass authorization or audit.

`requestId` is a correlation identifier. Mutating operations additionally need
an idempotency definition. A binding MAY use `requestId` as its idempotency key
only when it persists the first terminal result for the documented replay
window and rejects reuse with different canonical request bytes.

### 2.1 Binary values

A binding MUST identify the encoding of every binary value. The current HTTP
research profile uses canonical, unpadded base64 and rejects padding or
non-canonical input. A future binding may use native bytes, but its profile must
define an equivalent canonical representation for vectors and evidence hashes.

The API MUST NOT infer whether bytes represent a message, digest, ciphertext,
tag, nonce, public key, wrapped key, encapsulation, or context value.

### 2.2 Minimum constraints

A request MAY constrain:

- operation profile;
- acceptable provider classes;
- minimum security strength;
- required key protection and exportability;
- required assurance or attestation profile;
- jurisdiction or locality class;
- maximum policy age and capability age; and
- required algorithm or construction properties.

Constraints are minimums, not algorithm-selection hints. The broker MUST reject
unknown critical constraints and any decision that is weaker than a stated
minimum.

### 2.3 Common result

Every success returns the common response from the core specification plus one
typed operation result. Every mutating result includes the resulting resource
version or state. Every result involving a key includes the logical `keyRef` and
`keyVersion` unless policy requires redaction from the consumer view.

## 3. Discovery and policy

| Operation | Status | Input | Result |
| --- | --- | --- | --- |
| `GetCapabilities` | implemented | authenticated scope and optional profile/family filter | freshness-bounded profiles, operations, algorithms, provider classes, protection properties, and limitations |
| `ListProfiles` | specified | family or intent filter | profile identifiers, versions, maturity, and semantic summaries |
| `ResolvePolicy` | implemented | intent, operation, constraints, optional expected policy | exactly one pinned decision or explicit policy failure |
| `DryRunPolicy` | specified | proposed request plus evaluation context | non-executable decision explanation with redacted alternatives and conflicts |

Capability responses MUST include `generatedAt`, `validUntil` or an equivalent
freshness bound, scope, and provider identity or an authorized redaction token.
They MUST NOT reveal cross-tenant key existence or convert discovery into
authorization.

Policy resolution MUST return one profile, algorithm/construction identifier,
provider requirements, key requirements, policy provenance, and policy version.
Hierarchical evaluation MUST define precedence and conflict handling. Two
incompatible surviving decisions produce `POLICY_AMBIGUOUS`; ordering in a
configuration file is not an acceptable tie-breaker unless the policy language
normatively defines it.

## 4. Key operations

| Operation | Status | Required input | Result |
| --- | --- | --- | --- |
| `CreateKey` | implemented for signing | purpose and optional caller label | opaque `keyRef`, version, state, public material when applicable, and non-secret properties |
| `ReadKey` | implemented | `keyRef`, optional version | authorized non-secret metadata only |
| `ListKeys` | specified | bounded filter and pagination token | authorized metadata page; never private or secret material |
| `RotateKey` | specified | `keyRef`, expected active version, reason | new version under the logical reference and continuity disposition |
| `TransformKey` | specified | source reference/version, target profile constraints, reason | successor key reference/version plus predecessor relationship |
| `MigrateKey` | specified | source reference/version, target provider constraints, named strategy | resulting reference/version, custody evidence, and source disposition |
| `ImportKey` | specified | purpose, wrapped/protected material, source format and provenance | provider-owned reference and verified import properties |
| `ExportKey` | specified | reference/version, approved protection or wrapping profile | protected output only when policy and provider properties permit it |
| `SetKeyState` | specified | reference/version, expected state, target state, reason | new state and state version |
| `DestroyKey` | specified | reference/version, expected state, reason, authorization evidence | destruction receipt and residual-copy disposition |

### 4.1 Key state machine

Candidate states are `pre-active`, `active`, `suspended`, `deactivated`,
`compromised`, `destroy-pending`, and `destroyed`. Profiles MUST name the states
allowed for each operation. A stale expected version or state fails with
`KEY_STATE_INVALID`; it does not apply to the latest version automatically.

Rotation creates a new version of the same logical key. Transformation creates
successor key material when the algorithm family or representation changes.
Migration names exactly one strategy:

1. provider switch without key movement;
2. policy-authorized extract and import;
3. provider-to-provider wrapped transfer;
4. rekey and archive; or
5. rekey and destroy.

The result MUST state which strategy executed, what happened to the source, and
which old versions remain usable for verification or decryption. “Move key” is
not a portable strategy.

Import, export, compromise, revocation, and destruction require distinct
permissions. `DestroyKey` MUST NOT be inferred from rotation or migration and
MUST be idempotent for the same authorized request.

## 5. Signature and MAC operations

| Operation | Status | Required input | Result |
| --- | --- | --- | --- |
| `Sign` | implemented for message signing | signing `keyRef`, typed message | signature, signature encoding, key version |
| `Verify` | implemented for message signing | verification key reference or approved public key, typed message, signature | boolean `valid`; malformed input remains an error |
| `SignDigest` | specified | signing `keyRef`, digest value, digest algorithm identifier | signature and explicit prehash profile |
| `VerifyDigest` | specified | key/public material, digest value, digest identifier, signature | boolean `valid` and explicit prehash profile |
| `GenerateMac` | specified | MAC `keyRef`, typed message | tag, tag encoding, key version |
| `VerifyMac` | specified | MAC `keyRef`, typed message, tag | boolean `valid` |

Message signing and digest signing are different profiles. A provider MUST NOT
hash a `SignDigest` input again or treat a `Sign` message as a digest. Verification
returns `valid: false` for a well-formed cryptographic mismatch; malformed
encoding, unauthorized keys, and invalid key state remain explicit errors.

MAC verification SHOULD use a provider operation or constant-time comparison.
The response MUST NOT expose a computed comparison tag.

## 6. Encryption operations

| Operation | Status | Required input | Result |
| --- | --- | --- | --- |
| `Encrypt` | specified | encryption `keyRef`, plaintext, optional AAD, profile-approved nonce mode | profile-defined ciphertext package, key version |
| `Decrypt` | specified | decryption `keyRef`, ciphertext package, identical AAD context | plaintext only after complete authentication, key version |

Authenticated encryption is the default symmetric encryption profile. A
profile fixes whether ciphertext, nonce, and tag are separate or combined,
their ordering and lengths, and whether the nonce is provider-generated. A
caller-supplied nonce is allowed only by a profile that defines uniqueness
enforcement and failure behavior.

Plaintext MUST NOT be released before authentication succeeds. A well-formed
authentication failure uses `AUTHENTICATION_FAILED` and SHOULD avoid details
that create a decryption oracle. Retrying encryption is unsafe unless the
binding guarantees idempotent result replay; it MUST NOT repeat execution with
the same provider-generated nonce assumption.

Bounded asymmetric encryption requires a separate profile with message-size,
padding, label, and ciphertext rules. It is not an implicit mode of `Encrypt`.

## 7. Digest, XOF, and random operations

| Operation | Status | Required input | Result |
| --- | --- | --- | --- |
| `Digest` | specified | typed message | digest, encoding, resolved algorithm |
| `ExpandOutput` | specified | typed message and approved output length | output bytes, length, resolved XOF profile |
| `GenerateRandom` | specified | requested length and purpose | random bytes and generator profile evidence |

Policy MUST cap all output lengths. `GenerateRandom` output is raw random data,
not a key reference; keys must be created through `CreateKey` so purpose,
custody, lifecycle, and evidence are established. Retry creates new random output
unless the binding returns a stored idempotent result.

## 8. Derivation and key establishment

| Operation | Status | Required input | Result |
| --- | --- | --- | --- |
| `DeriveKey` | specified | base/secret key reference, typed salt/context, derived-key purpose | new provider-owned `keyRef` and derivation evidence |
| `DeriveBytes` | specified | base/secret key reference, typed salt/context, approved length | bytes only when policy allows secret export |
| `AgreeKey` | specified | local private `keyRef`, validated peer public key, context | provider-owned shared-secret `keyRef` |
| `Encapsulate` | specified | validated recipient public key and context | encapsulation plus provider-owned shared-secret `keyRef` |
| `Decapsulate` | specified | recipient private `keyRef`, encapsulation, context | provider-owned shared-secret `keyRef` |
| `WrapKey` | specified | wrapping `keyRef`, subject `keyRef`/version, wrap profile | wrapped object and protected metadata |
| `UnwrapKey` | specified | unwrapping `keyRef`, wrapped object, target purpose/properties | provider-owned subject `keyRef` and verified properties |

Shared secrets and derived keys remain provider-owned by default. Returning raw
secret bytes requires a profile and policy that explicitly permit export.
Agreement and KEM profiles MUST define public-key validation, context binding,
key-confirmation expectations, failure behavior, and how all-zero or otherwise
invalid shared secrets are handled.

A hybrid or composite establishment profile must define the complete reviewed
construction: component algorithms and parameters, input validation, combiner,
domain separation, byte encoding, partial failure, downgrade behavior, and
security assumptions. Concatenation is not a default CAAP combiner.

## 9. Streaming operations

`BeginOperation`, `UpdateOperation`, `FinalizeOperation`, and `AbortOperation`
are `reserved`. No portable streaming contract is claimed yet.

A streaming profile must define server-generated operation identifiers,
ordering, chunk and total limits, idle/absolute expiry, concurrency, replay,
abort, finalization, intermediate plaintext release, provider-session loss, and
cleanup. A binding MUST NOT emulate streaming by silently buffering unbounded
input.

## 10. Retry and idempotency defaults

| Class | Default |
| --- | --- |
| Read-only discovery, metadata, policy dry-run | retryable when authorization and freshness are re-evaluated |
| Verify, digest, MAC verify | retryable with identical canonical input and pinned policy |
| Create, rotate, transform, migrate, import, unwrap, state change, destroy | requires persistent idempotency result or explicit duplicate rejection |
| Sign and MAC generation | profile-specific; repeat may create multiple valid outputs |
| Encrypt, encapsulate, random generation | do not automatically re-execute after an unknown outcome |
| Decrypt, decapsulate, derive, agreement | retry only when the profile, key state, side-channel policy, and provider semantics permit it |

`PROVIDER_UNAVAILABLE` is not automatically retryable. The response and profile
must say whether execution could have occurred. A broker MUST NOT retry through
a different provider, algorithm, key version, or policy unless the original
decision explicitly authorized that route and preserves the operation profile.

## 11. Portable failures

The core failure categories apply to every operation. These refinements are
also required:

| Category | Meaning |
| --- | --- |
| `AUTHENTICATION_FAILED` | Well-formed ciphertext or protected object failed cryptographic authentication. |
| `STATE_CONFLICT` | An optimistic resource version or lifecycle precondition no longer holds. |
| `IDEMPOTENCY_CONFLICT` | An idempotency key was reused with different canonical request content. |
| `OUTPUT_RESTRICTED` | Policy or provider properties prohibit returning requested secret/key output. |
| `RATE_LIMITED` | Authorized request exceeded an enforced quota; retry metadata may be returned. |

Provider-native codes MAY appear only in an authorized diagnostic view. The
portable category controls consumer behavior and MUST remain stable across
providers.

## 12. Algorithm profile requirements

Every profile document MUST define:

1. identifier, version, maturity, and operation family;
2. exact input interpretation and canonical encoding;
3. output structure and canonical encoding;
4. algorithm or construction identifiers and parameter rules;
5. key type, purpose, states, protection, export, and version rules;
6. input, output, and resource limits;
7. provider capability fields and equivalence requirements;
8. policy constraints and authorization points;
9. idempotency, retry, timeout, and cancellation semantics;
10. evidence fields, privacy/redaction rules, and audit events;
11. positive, negative, boundary, and cross-provider vectors; and
12. security assumptions, failure refinements, and prohibited substitutions.

An algorithm catalog entry is not a profile. A profile is eligible for a
portable conformance claim only after its schemas, vectors, runner, and
independent implementation evidence exist.

## 13. Provider adapter contract

Provider adapters translate the resolved CAAP operation into a backend-native
operation; they do not reinterpret policy. Every adapter MUST:

- publish authenticated, freshness-bounded capabilities;
- identify the exact mechanism, algorithm, parameters, key properties, and
  provider instance used;
- preserve non-exportability, key purpose, lifecycle state, and tenant binding;
- map native errors to one stable CAAP category without discarding authorized
  diagnostic detail;
- reject unsupported parameters rather than emulate a weaker construction; and
- report whether a failed mutating operation could have completed.

An OpenSSL software adapter must pin library/provider configuration and expose
which implementation supplied the primitive. A PKCS#11 adapter must preserve
mechanism parameters, sessions, object attributes, token state, and native
return codes. A KMIP or cloud KMS adapter must preserve managed-object identity,
state, usage restrictions, extractability, activation, and native result
status/reason. A JCA bridge must distinguish algorithm names from provider
selection and must not make provider-order fallback a policy decision.

The adapter contract does not assert that two providers are equivalent. A
profile earns provider portability only through common vectors and materially
different implementations.

## 14. Policy templates and knowledge

A template catalog may describe operation profiles, algorithm properties,
security strength, deprecation status, provider requirements, protocol
compatibility, and regulatory source references. Each assertion needs a source,
effective date, catalog version, and review status. Descriptive catalog data is
not policy until an authorized policy authority incorporates it into a signed,
versioned decision.

Hierarchical organizational and regulatory profiles MUST define precedence,
intersection, exceptions, conflict failure, activation, expiry, withdrawal, and
provenance. A child policy cannot weaken a non-overridable parent minimum.
Declarative key evolution requires desired state, current state, dry-run,
approval, blast-radius reporting, idempotent reconciliation, staged rollout,
evidence, and rollback or compensating action where reversal is impossible.

## 15. Deployment invariants

Local-library, sidecar, remote-service, and hybrid control-plane deployments may
use different transports. All must preserve the authenticated caller and tenant,
pinned policy decision, scoped capability, key state/version, exact dispatch,
failure category, and evidence semantics.

An HTTP-to-gRPC gateway is a binding translator, not a second policy authority.
It must preserve status, binary encoding, timeouts, cancellation, streaming
boundaries, and stable error categories without converting a rejected operation
into a transport retry.

Caching policy or capabilities does not transfer ownership to the broker. Cache
entries require authenticated provenance, expiry, withdrawal behavior, and
rollback resistance. Persistent stores must encrypt sensitive metadata at rest,
separate key-encryption keys from stored data, and never treat the broker
database as a default private-key store.

Container and Kubernetes packaging must define non-root execution, immutable
image identity, dependency provenance, read-only filesystems where feasible,
secrets injection, network policy, readiness versus liveness, graceful drain,
resource bounds, audit export, and upgrade/rollback behavior. Packaging does not
change the cryptographic or policy contract.
