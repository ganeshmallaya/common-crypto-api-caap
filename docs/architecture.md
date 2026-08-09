# Architecture

Status: working research draft

## Logical model

```text
Consumer or CA workflow
          |
          | Common Crypto API: intent + operation + constraints
          v
      CALI broker  <---- authenticated policy ----> Policy authority
          |
          | provider operation + resolved choice
          v
   Provider adapter <---- scoped capability ----> Crypto backend
          |
          +-- software library
          +-- HSM
          +-- KMS
          +-- key store
```

The model has a northbound consumer contract and a southbound provider
contract. The broker connects them but does not make an unconstrained “best
available” choice. It applies an authenticated policy decision and rejects a
request when the decision, capabilities, or caller constraints do not agree.

## Component responsibilities

### Consumer

- Authenticates to the CALI deployment.
- Names an intent and operation.
- Supplies required context and non-negotiable constraints.
- Keeps request identifiers stable across safe retries.
- Does not rely on an undocumented fallback.

### Broker

- Authenticates and authorizes the caller.
- Validates request shape, version, freshness, and replay controls.
- Pins the policy profile and version used for a decision.
- Checks that provider capability and key metadata match the decision.
- Routes the operation and returns a structured result or error.
- Emits security-relevant audit events without secrets.

The broker is a policy enforcement point, not the unconstrained policy decision
maker or a source of cryptographic truth. It has bounded operational
intelligence: it validates context, matches authenticated capabilities, routes
operations, manages logical references, and records evidence. The policy
authority owns the risk decision. The broker does not make an algorithm secure
merely by selecting it.

### Policy authority and resolver

- Publishes versioned profiles with provenance and lifecycle state.
- Evaluates intent, operation, caller context, and minimum constraints.
- Returns one unambiguous decision or a rejection.
- Supports staged evaluation before activation.

The mechanism for authenticating policy profiles is unresolved. Until it is
specified, a deployment cannot claim downgrade-resistant policy distribution.

### Provider adapter

- Translates provider-interface operations to one backend.
- Reports scoped capability information.
- Preserves key protection and authorization properties.
- Maps provider failures to CALI error categories without hiding detail needed
  for operators.

Capability discovery is not authorization and does not guarantee that a later
operation will succeed.

A provider adapter may translate the southbound contract to PKCS#11, OASIS
KMIP, a cloud KMS API, or a software-library API. That translation must preserve
operation, parameter, object-state, authorization, key-custody, and error
semantics. CALI does not replace the underlying provider protocol. See
[`control-plane-and-kmip.md`](control-plane-and-kmip.md).

### Certificate authority integration

A CA or certificate management workflow is normally a consumer or orchestrator
at the north boundary. It can ask CALI to generate or use a key and to perform a
signature. CALI does not decide certificate subject policy, validate an
enrollment request, issue a certificate, publish revocation state, or replace
ACME, CMP, EST, or other CA protocols.

## Trust boundaries

1. **Consumer to broker:** caller identity, request integrity, tenant isolation,
   freshness, and authorization.
2. **Broker to policy authority:** policy provenance, version pinning, rollback
   prevention, availability, and consistent time.
3. **Broker to provider:** mutual authentication where remote, capability
   authenticity, operation authorization, key-reference scoping, and error
   integrity.
4. **Provider to backend:** backend credentials, key custody, mechanism
   translation, session isolation, and lifecycle state.
5. **Research repository to hosted research site:** reviewed native explanatory
   pages, direct authoritative-source links, branch protection, build
   provenance, and explicit publication approval.

## Deployment patterns

| Pattern | Benefit | Important boundary |
| --- | --- | --- |
| In-process library | Low call overhead | Application compromise may include the broker and software keys. |
| Local daemon or sidecar | Language-neutral local contract | Local peer authentication and namespace isolation become critical. |
| Central service | Central policy and audit | Network identity, availability, latency, and cross-tenant isolation become critical. |
| Tiered deployment | Local operations with central governance | Policy consistency, cache expiry, and disconnected behavior must be defined. |

No pattern is selected as the canonical deployment in this phase.

## Hard boundaries

- CALI does not make a backend more secure than its implementation and
  operating controls.
- A key reference does not prove hardware protection.
- A capability statement is not a conformance certificate.
- Combined algorithms require explicit construction and encoding definitions;
  the broker cannot safely invent them.
- Constrained or fixed-function environments may require build-time choices and
  may not support the broker model.
