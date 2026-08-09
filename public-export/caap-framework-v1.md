# A Common Crypto API: Research Framework v1

One application call can carry several decisions that belong to different
owners. A developer needs a signature, but the call may also select the
algorithm, parameters, library, provider, key-store structure, and encoding.
The application then owns choices that security policy, infrastructure, and
the cryptographic backend should be able to control independently.

A Common Crypto API starts by separating those decisions. The application asks
for a defined operation. It does not need to know which device, service,
library, or provider-specific mechanism performs it.

The Crypto Agility Algorithm Protocol (CAAP) is my research into that missing
abstraction layer. CAAP defines the control and interaction boundaries. The
Common Crypto API is the interface an application consumes.

This is an exploratory framework, not a standard and not a product claim. Its
purpose is to make the idea precise enough to test.

![CAAP cryptographic abstraction layer](images/caap-abstraction-layer.svg)

## The idea in one sentence

A consumer states an operation, intent, typed input, and constraints; a broker
enforces a separate policy decision and dispatches the exact operation through
a common provider interface.

The model has two contracts.

The northbound contract is the Common Crypto API. Applications depend on this
contract. It describes operations such as key-pair generation, signing,
verification, encapsulation, and decapsulation without exposing a vendor or a
backend location.

The southbound contract is the provider service-provider interface. Software
libraries, HSMs, KMSs, key stores, PKCS#11 adapters, and KMIP adapters implement
this side.

The broker sits between them. It validates the request, obtains one policy
decision, checks key state and provider capability, dispatches the operation,
and returns a typed result or an explicit failure.

## What the application says

“Intent-based” cannot mean that the application sends a vague label and hopes
the infrastructure makes a good choice. The intent must belong to an operation
class with defined input and output semantics.

A signing request, for example, must say whether its input is a message,
digest, or structured object. It can require that a key remain non-exportable.
It can pin an expected policy version. It should not name an HSM slot, KMIP
object, cloud KMS endpoint, or software library.

That distinction matters. Two algorithms are not interchangeable merely
because both produce something called a signature. They are substitutable for
a given intent only when the operation shape, encoding, caller constraints,
and verifier expectations remain compatible.

## Policy decides. The broker enforces.

I separate the policy authority from the broker deliberately.

The policy authority owns decision intelligence. It evaluates the
authenticated context, operation, intent, minimum constraints, effective time,
and approved policy. Its output is one pinned decision or one rejection.

The broker owns bounded operational intelligence. It authenticates and
authorizes, resolves an opaque key reference, checks current capability and key
state, selects an allowed provider, and dispatches exactly what the decision
permits.

The broker must not quietly pick the “next best” algorithm. If policy is
ambiguous, expired, or incompatible with available providers, the result is a
specific failure.

![CAAP request and execution flow](images/caap-request-flow.svg)

This division also makes the architecture implementable by more than one
vendor. One product may provide policy authoring and approvals. Another may
operate the broker. A cloud service, HSM, or key manager may implement the
provider side. An integrated product can implement all three, but the
observable contracts remain the same.

## The initial Common Crypto API surface

Framework v1 starts with a deliberately small operation set:

- `GetCapabilities` returns a caller-scoped description of the Common Crypto
  API capabilities. It is not authorization.
- `ResolvePolicy` evaluates a request without executing cryptography.
- `GenerateKeyPair` resolves creation intent and returns an opaque key
  reference with non-secret metadata.
- `Sign` and `Verify` operate on explicitly typed inputs.
- `Encapsulate` and `Decapsulate` perform key-establishment operations with an
  explicit secret-delivery model.

Authenticated encryption, key derivation, wrapping, import, export,
destruction, streaming, and successor-key operations are reasonable
extensions. I have left them out of the base profile until their authorization,
retry, and data semantics can be defined without hand-waving.

## Opaque references are not security claims

The consumer holds a logical key reference. It does not see a slot identifier,
file path, KMIP Unique Identifier, or provider credential.

That opacity is useful, but it proves nothing by itself. A logical reference
does not prove that a key is hardware protected, non-exportable, attested, or
portable. Those properties must appear as explicit requirements and must be
supported by defined evidence.

The same caution applies to provider substitution. A non-extractable key may
not be movable. A provider may not preserve the required operation semantics.
The abstraction layer must expose that mismatch rather than conceal it.

## Where PKCS#11 and KMIP fit

CAAP sits above existing provider protocols. It does not replace them.

A PKCS#11 adapter can translate the provider contract into token sessions,
mechanisms, objects, and attributes. A separate compatibility module might
present the broker as a PKCS#11 token for existing applications, but that is a
reduced binding. It cannot be assumed to carry every intent and constraint.

A KMIP adapter can map provider operations to managed objects, attributes,
profiles, and cryptographic operations. The broker resolves the consumer's
intent before dispatch. KMIP continues to define its own wire protocol and
managed-object semantics.

This is one of the areas I want CAAP to test directly: which mappings preserve
meaning across implementations, and which mappings lose information that the
consumer or policy must see?

## Combined cryptography needs more than orchestration

A broker may eventually dispatch parts of a defined combined construction to
different providers. That does not give the broker authority to create a new
construction.

Before a combined operation can be interoperable, a reviewed definition must
fix the constituent algorithms, parameter sets, combination rule, byte
encoding, verification behavior, partial-failure behavior, and security
assumptions. Running two algorithms and concatenating their outputs is not a
specification.

## What should be open

The value of a common API depends on more than prose. The portable layer should
include operation semantics, the policy decision contract, provider behavior,
error categories, evidence fields, versioning rules, adapter profiles, test
vectors, and negative tests.

That leaves substantial room for vendors to build products.

![Open CAAP contract and vendor implementation boundary](images/caap-open-vendor-boundary.svg)

Policy editors, packaged policy content, SDKs, adapters, low-latency routing,
availability, key custody, hardware assurance, attestation, analytics,
orchestration, managed services, and support are all implementation and
commercial opportunities. A common contract reduces integration friction; it
does not make those systems interchangeable commodities.

## How this relates to IBM and CCP

IBM Research has published an intent-based cryptographic API design built
around scopes, policy, providers, stable key identifiers, and key-evolution
operations. Its central argument is that applications should state what they
need while the abstraction layer determines how and where the operation runs.

The Cryptographic Control Plane working draft describes the broader enterprise
control-plane architecture. Its own open questions include the standardized
API contract, conformance, reference implementation, integration with existing
standards, and deployment patterns.

I am not claiming those ideas as CAAP inventions. CAAP concentrates on the seam
I want to make independently testable: a small consumer contract, a provider
contract, a policy-decision boundary, broker enforcement, portable failures,
decision evidence, and explicit PKCS#11 and KMIP mappings.

Whether that seam is sufficiently different or useful is a research question,
not a conclusion.

## The first test

The next useful artifact is not a larger architecture diagram. It is a narrow
interoperability demonstration.

I propose starting with artifact signing. One consumer sends the same request
to a broker. The broker resolves one policy and can dispatch to two materially
different providers: one software provider and one PKCS#11- or KMIP-backed
provider. The test publishes successful vectors and explicit failures for
policy ambiguity, constraint mismatch, invalid key state, and missing provider
capability.

If an independent implementation cannot reproduce those results, the contract
is not ready. That is the standard this research should meet before it asks an
industry group to adopt anything.

## References

- [IBM Research: It is time for cryptography to get its own abstraction layer](https://research.ibm.com/blog/cryptography-abstraction-layer)
- [An Assessment Framework for Application-Level Cryptographic Agility](https://arxiv.org/abs/2606.13425)
- [Intent-Based Cryptographic API Design for Cryptographic Agility](https://arxiv.org/abs/2606.13445)
- [Cryptographic Control Plane Standard, version 0.9 working draft](https://ccp-standard.org/)
- [NIST CSWP 39 update 1](https://csrc.nist.gov/pubs/cswp/39/upd1/considerations-for-achieving-crypto-agility/final)
- [OASIS KMIP Specification Version 2.1](https://docs.oasis-open.org/kmip/kmip-spec/v2.1/os/kmip-spec-v2.1-os.html)
