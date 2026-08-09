# Broker, policy, and KMIP boundaries

Status: working research draft

## Architectural answer

The broker should be intelligent enough to enforce a decision, but it should
not be the unconstrained author of that decision.

```text
Enterprise risk owner
        |
        | approves objectives, exceptions, and rollout
        v
Policy authority / decision point
        |
        | signed, versioned, unambiguous decision
        v
CALI broker / enforcement point
        |
        | concrete operation and constrained provider request
        v
Provider adapter ----> PKCS#11, KMIP, KMS API, library, or key store
```

The policy authority is the **decision intelligence**. The broker is the
**operational intelligence and enforcement point**. It performs contextual
validation, capability matching, routing, handle resolution, safe retry
handling, and evidence generation. It does not invent organizational risk
policy, rank algorithms from first principles, or silently optimize around a
rejection.

This separation makes decisions reviewable and makes more than one broker
implementation possible.

## Who owns what

Ownership has two meanings and they should not be collapsed.

### Governance ownership

The deploying enterprise owns:

- risk appetite and protected-purpose definitions;
- approved algorithms, providers, assurance levels, and exceptions;
- effective dates, rollout waves, emergency actions, and rollback authority;
- separation of duties and final approval; and
- acceptance of protocol, verifier, data-migration, and availability risk.

Industry bodies and public specifications can define vocabulary and
interoperability rules. They cannot make a risk decision for an enterprise.

### Software ownership

A vendor, cloud provider, open-source project, or enterprise platform team may
implement the policy engine or broker. No single ownership model is mandated.
Portable policy inputs, decision outputs, audit records, and conformance tests
are the protection against that implementation becoming the standard.

A practical deployment may use one vendor for policy authoring, another for a
broker, and several providers. It may also use one integrated vendor product.
Both should satisfy the same observable contracts.

## Policy framework responsibilities

The open policy framework should define:

- stable intent and operation vocabulary;
- authenticated decision inputs and their trust source;
- rule applicability, priority, conflict, and ambiguity semantics;
- algorithm and construction identifiers with external registry references;
- provider-class and key-protection constraints;
- minimum security and interoperability constraints;
- effective, expiry, deprecation, withdrawal, and exception lifecycle;
- profile version, provenance, signature, trust anchor, and rollback rules;
- one decision or explicit rejection as the output;
- explanation data sufficient to reproduce and audit a decision;
- evaluation, simulation, staged activation, and compatibility-test behavior;
  and
- privacy rules for context and decision records.

An open framework should not standardize a vendor's policy editor, risk score,
workflow UI, approval product, analytics model, or content library. Those are
valid areas of differentiation.

## Broker responsibilities

For one operation, a conforming broker needs to preserve this sequence:

1. Authenticate the caller from a trusted channel or workload identity.
2. Establish tenant, workload, environment, and authorization context.
3. Validate the API version, operation, intent, request identifier, freshness,
   payload type, and non-negotiable constraints.
4. Authorize the intent and operation before exposing provider information.
5. Request a decision from an identified policy authority or evaluate an
   authenticated, pinned profile.
6. Reject missing, inactive, ambiguous, unsigned, rolled-back, or incompatible
   policy.
7. Resolve a logical key reference, if present, to authorized provider state.
8. Match the decision against fresh-enough, authenticated, scoped provider
   capabilities and key metadata.
9. Dispatch exactly one permitted operation, or dispatch a separately defined
   combined construction; never invent a fallback or composition.
10. Normalize the outcome without discarding provider detail needed by an
    authorized operator.
11. Return the policy, algorithm, provider, key, and timing references needed
    for audit, subject to disclosure policy.
12. Emit a tamper-evident event that contains no secret key material or
    unintended sensitive payload.

Caching, load balancing, health checks, queuing, and route selection are broker
functions. A cached policy decision remains bound by provenance, expiry,
rollback, and disconnected-operation rules.

## Common Crypto API behavior by operation

Policy does not have the same effect on every operation. The distinction below
prevents “one policy change” from becoming a claim that existing keys change
their mathematics in place.

| Operation class | Policy and broker behavior |
| --- | --- |
| `GetCapabilities` | Returns a caller-scoped view of possible operations and constraints; it does not authorize a later operation. |
| `ResolvePolicy` | Evaluates without executing and returns the pinned decision or rejection needed for planning and tests. |
| `GenerateKeyPair` | Policy may select an allowed algorithm, provider class, key properties, and lifecycle requirements. The result is an opaque reference bound to the created key state. |
| `Sign`, `Decapsulate`, or another private-key operation | The key's algorithm cannot change for this call. Policy authorizes the operation and confirms that the handle, algorithm, provider, and context remain allowed. |
| `Verify` or public-material operations | The input format may require an explicit algorithm or construction identifier for safe interpretation. Intent does not remove protocol encoding requirements. |
| Successor-key migration | Orchestration creates or imports a new key, proves the required relationship, updates an authorized logical alias if used, coordinates certificates and verifiers, and retains lineage. This is not an ordinary signing call. |

The candidate envelope in
[`protocol-envelope.schema.json`](../schemas/protocol-envelope.schema.json)
provides a request identifier, version, operation, intent, expected-policy pin,
minimum constraints, and typed operation input. The response provides outcome,
policy and algorithm references, provider reference, result, or a structured
error. The schema is experimental and does not yet define a normative wire
binding.

## Is the broker the main intelligence?

No single component should hold all intelligence.

| Question | Primary component |
| --- | --- |
| What risk is acceptable for this purpose? | Enterprise governance and policy authority |
| Which decision applies to this authenticated context? | Policy decision point |
| Can the decision be executed now and where? | Broker using authenticated capability and key state |
| How is the cryptographic operation performed? | Provider and backend |
| Which assets and dependencies must migrate? | Inventory and orchestration systems |
| Did the intended change occur? | Broker telemetry plus independent observation |

The broker is therefore more than a proxy but less than an autonomous security
authority. Its intelligence is constrained, deterministic, and explainable.

## KMIP relationship

KMIP is complementary and should be a first-class southbound integration.
OASIS KMIP defines client-server operations for managed objects such as keys
and certificates. Its profiles cover key lifecycle and cryptographic services,
including encryption, decryption, signing, and verification. KMIP requests can
carry concrete cryptographic algorithms and parameters.

CALI operates one layer above that contract:

| CALI concept | KMIP relationship |
| --- | --- |
| Intent, such as `artifact-signing` | Not replaced by a KMIP object name or operation-policy name; resolved before dispatch |
| Policy decision | Selects the permitted algorithm, parameters, assurance, and provider class |
| Logical key reference | Broker-owned opaque reference mapped to a KMIP Unique Identifier within an authorized provider context |
| Capability descriptor | May be populated from KMIP Query, profile, capability, and managed-object information, then scoped and authenticated by the adapter |
| Key generation and lifecycle | Adapter maps approved CALI operations to KMIP Create, Create Key Pair, Re-key, Register, Destroy, or related operations when their semantics match |
| Cryptographic execution | Adapter maps to KMIP Encrypt, Decrypt, Sign, Signature Verify, MAC, or other supported operations |
| Provider error | Adapter preserves KMIP result status and reason for operators while mapping it to a stable CALI error category |

The adapter must not translate by name alone. It must check operation
semantics, algorithm and parameter identifiers, object state, usage mask,
extractability, activation dates, tenant authorization, and provider profile.

### What CALI must not claim about KMIP

- CALI does not replace KMIP's managed-object lifecycle or wire protocol.
- A KMIP server's support for an operation does not prove the caller is allowed
  to use a particular object.
- A KMIP Unique Identifier is not automatically a portable CALI key reference.
- Re-keying does not mean an asymmetric private key can be mathematically
  converted into a different algorithm. Cross-algorithm migration normally
  creates a successor key and records continuity at the logical-reference or
  application-identity layer.
- A provider migration may be impossible when the source key is
  non-extractable. CALI must return that constraint, not hide it.

## Recommended implementation split

The open CALI work should own the northbound and southbound semantics, policy
decision contract, minimum audit vocabulary, failure behavior, and conformance
tests. An initial reference implementation should include a small broker and a
KMIP adapter, but should not become the only valid implementation.

Vendors should own production policy engines, broker deployments, adapters,
high availability, user experience, migration orchestration, assurance, and
support. Enterprises should retain approval of active policy and trust anchors.

## Sources

- [OASIS KMIP Specification Version 2.1](https://docs.oasis-open.org/kmip/kmip-spec/v2.1/os/kmip-spec-v2.1-os.html)
- [OASIS KMIP Profiles Version 2.1](https://docs.oasis-open.org/kmip/kmip-profiles/v2.1/os/kmip-profiles-v2.1-os.html)
