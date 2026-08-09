# Problem statement

Status: working research draft

## The coupling problem

Applications commonly make cryptographic choices in several places at once:
source code, library configuration, certificate profiles, HSM or KMS adapters,
key-store identifiers, protocol settings, and deployment automation. An
algorithm or provider transition can therefore become many application changes
rather than one governed policy change.

The problem is broader than selecting an algorithm. A safe decision depends on
the operation, data or identity being protected, protocol constraints, key
location, provider capabilities, organizational policy, lifecycle dates, and
the caller's authorization. Hiding only the library API does not remove these
dependencies.

## Research hypothesis

CAAP explores whether a stable Common Crypto API can accept an operation intent
and resolve it through versioned policy to an allowed algorithm and provider.
The provider might be a software library, HSM, KMS, or key store. A certificate
authority can use the API as part of an issuance workflow without CAAP taking
over certificate lifecycle semantics.

A successful abstraction would make supported transitions policy-led while
keeping the decision visible, attributable, testable, and reversible. It must
not turn algorithm agility into an opaque fallback mechanism.

The central research object is the abstraction layer itself: the consumer
contract, provider contract, policy-decision boundary, broker enforcement
behavior, and evidence required for two implementations to behave consistently.
Inventory, migration orchestration, and certificate lifecycle systems may use
that layer, but they are not the CAAP thesis.

## Goals

- Separate application intent from algorithm and provider selection.
- Make policy identity, version, decision inputs, and result observable.
- Discover provider capabilities before an operation is dispatched.
- Keep key material opaque to callers unless a separately authorized operation
  explicitly permits export.
- Support classical, post-quantum, and combined approaches without making
  security or interoperability claims before they are specified and tested.
- Define stable failure categories for ambiguity, incompatibility, expiry,
  revocation, unavailability, and downgrade rejection.
- Allow local, sidecar, and service deployments to share the same conceptual
  contract while documenting their different trust assumptions.

## Non-goals for the initial research phase

- Defining a new cryptographic algorithm, certificate format, or identifier
  registry.
- Replacing PKCS#11, KMIP, platform KMS APIs, CA enrollment protocols, or
  certificate lifecycle management.
- Selecting a standards venue or claiming standards-track status.
- Claiming universal coverage for constrained devices, boot roots, or line-rate
  cryptographic datapaths.
- Defining a certification program or claiming conformance.
- Treating one experimental transport binding as the complete protocol.

## Evaluation questions

1. Can two independent implementations interpret an intent and failure in the
   same way?
2. Can policy change without application redeployment while remaining pinned,
   authenticated, and auditable?
3. Can a caller state non-negotiable security constraints without naming a
   provider-specific mechanism?
4. Can the broker prove which policy and capability information informed a
   decision?
5. Can provider substitution occur without changing operation semantics or
   weakening key-protection requirements?
6. Which cryptographic workflows cannot safely fit this abstraction?

The current artifact-signing slice supplies initial schemas, a reference
implementation, and negative tests. It does not answer the independent-
implementation, portability, or conformance questions.
