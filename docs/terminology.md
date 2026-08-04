# Terminology

Status: working research draft

The terms below are local working definitions. They do not create or override
definitions in external standards.

| Term | Working definition |
| --- | --- |
| **CAAP** | Crypto Agility Algorithm Protocol, the research specification for policy-controlled cryptographic operation selection and dispatch. |
| **Common Crypto API** | The consumer-facing interface defined by CAAP. |
| **Consumer** | An application or service that requests a cryptographic operation. |
| **Intent** | A stable, application-level purpose such as `artifact-signing`; it is not an algorithm name. |
| **Operation** | A requested action such as capability discovery, key generation, signing, verification, encapsulation, or decapsulation. |
| **Policy profile** | A versioned set of rules that maps an authorized intent and context to permitted choices. |
| **Policy decision** | The explicit result of evaluating an intent, context, constraints, policy version, and current lifecycle state. |
| **Broker** | The component that validates a request, obtains a policy decision, checks capabilities, and dispatches an operation. |
| **Provider** | An adapter that performs operations through a software library, HSM, KMS, key store, or another cryptographic backend. |
| **Provider interface** | The southbound contract a provider adapter implements. |
| **Capability descriptor** | An authenticated, scoped description of operations and identifiers a provider can support. It is not proof that a particular request is authorized. |
| **Algorithm identifier** | An identifier interpreted within an explicitly named registry or namespace. CAAP should reuse established identifiers where applicable. |
| **Combined algorithm** | A reviewed construction that uses more than one primitive with defined composition and encoding. “Hybrid” and “composite” are not treated as interchangeable without a cited definition. |
| **Key reference** | An opaque identifier for key material and its relevant metadata; it is not the key material itself. |
| **Caller context** | Authenticated identity, tenant, workload, purpose, environment, and other inputs used for authorization and policy. |
| **Minimum constraints** | Caller- or policy-supplied requirements that cannot be weakened during resolution. |
| **CA integration** | The boundary where a certificate authority or certificate workflow consumes cryptographic operations. CAAP does not define issuance or revocation semantics. |
| **HSM** | Hardware security module. Product-specific capability is not implied. |
| **KMS** | Key management service. Product-specific capability is not implied. |
| **Key store** | A system that retains keys or key references and enforces access or lifecycle controls. |
| **Public export** | Reviewed content copied from `public-export/` to a separate public website at a pinned repository commit. |

## Normative language

Capitalized requirement words are avoided during the exploratory phase. If a
later draft uses formal normative language, it must declare the convention and
the exact document scope to which it applies.
