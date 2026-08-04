# Common Crypto API — Draft Specification v0.1

**Status:** Working draft / strategy input — not submitted to any standards body
**Scope:** High-level architecture and requirements for a vendor-neutral, algorithm-agnostic cryptographic operations API supporting classical, post-quantum, and hybrid/composite algorithms
**Audience:** PKI/CLM vendors, HSM/KMS vendors, protocol implementers, standards reviewers

---

## 1. Abstract

This document specifies a vendor-neutral API for invoking cryptographic operations — signing, verification, key encapsulation, key derivation — without the calling application binding to a specific algorithm at compile time. Algorithm selection is resolved at call time against an external, centrally managed policy. The API is designed to remain stable across the transition from classical to post-quantum and hybrid cryptography, so that a single application integration survives multiple algorithm generations.

This is distinct from, and sits one layer above, existing hardware-abstraction APIs (e.g., PKCS#11). Where PKCS#11 abstracts *which token* performs an operation, this specification abstracts *which algorithm* performs it.

## 2. Motivation

Organizations operating multiple product lines or protocol integrations (TLS, X.509/CMP, SSH, JOSE/COSE, code signing) currently embed algorithm assumptions directly into application and product code. As the industry migrates to post-quantum and hybrid/composite cryptography under mandated deprecation timelines for classical algorithms, every one of those integrations becomes a separate migration project. This specification exists to convert future algorithm transitions from a code-change problem into a configuration-change problem, consistent with the crypto-agility approach described in NIST CSWP 39.

## 3. Terminology

| Term | Definition |
|---|---|
| **Operation** | A cryptographic action requested by a caller (e.g., Sign, Verify) independent of algorithm |
| **Algorithm Identifier** | A stable, registered identifier for a specific algorithm or parameter set |
| **Composite Identifier** | An identifier representing two or more algorithms combined (hybrid/composite) with a defined combiner |
| **Policy Profile** | A versioned, machine-readable document resolving an operation intent to a concrete Algorithm Identifier |
| **Provider** | An implementation of the backend interface (software library, HSM, KMS) that executes operations |
| **Capability Descriptor** | A machine-readable statement of what a Provider supports |
| **Conformance Level** | A defined subset of this spec a Provider or consumer claims to implement |

## 4. Non-Goals

- This specification does **not** define new cryptographic algorithms.
- This specification does **not** replace PKCS#11, TPM interfaces, or cloud KMS APIs — Providers may be implemented on top of any of these.
- This specification does **not** define UI/UX for any consuming product.
- This specification does **not**, in v0.1, mandate a single wire transport — it defines one normative binding (§10.1) and requirements for any additional binding.

## 5. Architecture Overview

```
Consumer Application
        |
        v
  Common Crypto API  <---- resolves via ---->  Policy / Agility Engine
        |
        v
  Provider Interface
        |
        v
  Crypto Backend (software, HSM, TPM, KMS)
```

The API (§7–8) is the only surface consumer applications integrate against directly. The Policy Engine and Provider Interface are internal to a Common Crypto API implementation and are not required to be exposed to the consumer.

## 6. Design Principles

1. **Operation-based, not algorithm-based.** Every API call names an operation (Sign, Verify, Encapsulate...); the algorithm is always a resolved parameter, never hardcoded by the caller.
2. **Hybrid/composite as first-class.** A Composite Identifier MUST be dispatchable to multiple underlying primitives plus a combiner function without special-casing at the call site.
3. **Policy-mechanism separation.** Algorithm resolution logic MUST live outside application code, in a versioned Policy Profile.
4. **Capability negotiation before execution.** A consumer MUST be able to query what a Provider supports before issuing an operation.
5. **Opaque key material by default.** Keys are referenced by handle; raw export requires an explicit, separately authorized operation.
6. **Fail closed on ambiguity.** If policy resolution is ambiguous or a required capability is absent, the API MUST return an explicit error rather than silently falling back to a default algorithm.

## 7. Core Object Model

### 7.1 Algorithm Identifier
- MUST be a stable string or integer registered in an external registry (see §9), never a vendor-private value for any algorithm intended to interoperate across implementations.
- Composite Identifiers MUST declare their constituent identifiers and combiner method explicitly, not implicitly via naming convention.

### 7.2 Key / Credential Handle
- Opaque reference. MUST NOT leak backend-specific structure (e.g., HSM slot IDs) to the caller.
- MUST carry: creation time, associated Algorithm Identifier(s), and current lifecycle state (active, deprecated, revoked).

### 7.3 Capability Descriptor
- Returned by a Provider on request. MUST enumerate: supported operations, supported Algorithm/Composite Identifiers, hardware-backed vs. software, and maximum key/message sizes.

### 7.4 Policy Profile
- Versioned document mapping an **intent** (e.g., `"tls-server-signing"`) to a resolved Algorithm or Composite Identifier, plus effective/expiry dates and a deprecation state.
- MUST be independently versionable from the API implementation itself — a policy update MUST NOT require redeploying the API.

## 8. Required Operations (Conformance Level 0 — mandatory)

| Operation | Description |
|---|---|
| `GetCapabilities()` | Returns the Capability Descriptor for the calling context |
| `GenerateKeyPair(intent)` | Resolves intent via policy, generates a key pair, returns a handle |
| `Sign(handle, message)` | Signs using the algorithm bound to the handle |
| `Verify(handle_or_public_material, message, signature)` | Verifies a signature |
| `Encapsulate(handle)` | KEM encapsulation, returns ciphertext + shared secret |
| `Decapsulate(handle, ciphertext)` | KEM decapsulation |
| `ResolvePolicy(intent)` | Returns the Algorithm/Composite Identifier that would be used, without performing the operation — required for dry-run/audit tooling |

Conformance Level 1 (optional) adds: `DeriveSecret`, `Wrap`/`Unwrap`, and mandatory support for at least one Composite Identifier.
Conformance Level 2 (optional) adds: hardware-backed key non-extractability guarantees and FIPS-validated backend attestation.

## 9. Algorithm Identifier Registry

- **Recommendation:** identifiers are drawn from existing IANA registries (e.g., COSE Algorithms) wherever an equivalent already exists, extended via standard IETF registration process for gaps (composite/hybrid identifiers specific to this API).
- This specification does **not** stand up a competing registry. See governance discussion (§14).
- Composite Identifiers require a registration entry declaring: constituent identifiers, combiner algorithm, and byte-level encoding of the combined output.

## 10. Bindings

### 10.1 Normative binding: RPC service
A conformant implementation MUST expose the operations in §8 as an RPC service defined by a machine-readable interface definition (IDL) — e.g., Protocol Buffers or an equivalent schema — published alongside this specification, not left to prose description. The IDL is what actually prevents vendor-to-vendor drift; the prose spec alone is not sufficient (see §14).

### 10.2 Optional binding: native library
Implementations MAY additionally expose a C-ABI or language-native binding for in-process/low-latency use (HSM-adjacent contexts). Native bindings MUST be semantically identical to the RPC binding — no capability may exist in one binding and not the other.

## 11. Error Handling

- Errors MUST be structured (code + machine-readable category + human message), not free-text only.
- Minimum required error categories: `UNSUPPORTED_ALGORITHM`, `POLICY_AMBIGUOUS`, `POLICY_EXPIRED`, `CAPABILITY_MISMATCH`, `HANDLE_REVOKED`, `PROVIDER_UNAVAILABLE`.
- Silent fallback to a default algorithm on error is explicitly prohibited (§6.6).

## 12. Versioning & Extensibility

- API version and Policy Profile version are independent and both explicit in every request/response.
- New operations and Composite Identifiers MUST be addable without breaking existing conformant clients (additive-only evolution within a major version).
- A major version bump is required only for breaking changes to the operation semantics defined in §8.

## 13. Security Considerations

- Policy Profiles are a high-value tampering target — integrity and provenance of the profile itself (signing, source authentication) is in scope for a future revision and MUST NOT be left undefined in the final spec.
- Capability Descriptors MUST NOT be trusted for security-relevant decisions unless obtained over an authenticated channel from the Provider.
- Downgrade resistance: policy resolution MUST be able to reject a request that would resolve to a weaker algorithm than the caller's minimum stated requirement, even if a weaker algorithm is technically available.

## 14. Conformance, Interoperability & the Role of Code

A prose specification is necessary but not sufficient for multi-vendor interoperability. To make this workable across every vendor, the following artifacts are required **alongside** this document, not instead of it:

1. **Machine-readable interface definition (IDL)** — normative, versioned, published in the same repository as the spec. Prevents each vendor from independently interpreting request/response shapes.
2. **Test vectors** — known-input/known-output pairs for every mandatory operation and at least one Composite Identifier, so implementations can be checked byte-for-byte, not just "believed correct."
3. **Reference implementation** — one open-source implementation of both a Provider and a consumer client, proving the spec is actually buildable as written. Ambiguities surface here before they surface in the field.
4. **Conformance test suite** — a runnable suite any vendor can execute against their own implementation to self-certify against a stated Conformance Level (§8).
5. **Certification/attestation program** — a later-stage, separately governed activity (see governance note below) that gives enterprise buyers a trust signal beyond "we read the spec."

Without items 1–4, this remains a design document that different vendors will implement differently in the exact places it matters most (edge cases, error semantics, composite encoding) — which recreates the fragmentation this API is meant to solve.

## 15. Governance Note (non-normative)

Recommended split, consistent with prior architecture discussion:
- **Algorithm identifiers:** IANA/IETF registration process — no new registry.
- **This specification + IDL + policy schema:** open multi-vendor consortium (e.g., Linux Foundation-hosted technical committee), since this is enterprise policy/product shape, not wire-protocol territory.
- **Conformance testing/certification:** separately governed lab or NCCoE-adjacent program, kept independent from the spec authors.

## 16. Open Issues for Working Group

- Exact IDL choice (protobuf vs. OpenAPI vs. CDDL) — affects both bindings and tooling ecosystem.
- Policy Profile signing/provenance mechanism (§13) — currently flagged, not designed.
- Whether Conformance Level 2 hardware-attestation requirements reference existing FIPS 140-3 language or require new attestation format.
- Backward compatibility story for consumers built against Level 0 when a Provider only offers Level 1+.

## 17. References

- NIST CSWP 39, *Considerations for Achieving Crypto Agility: Strategies and Practices*
- FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
- IANA COSE Algorithms Registry
- PKCS#11 (OASIS Cryptographic Token Interface)

---
*End of draft v0.1. This is a strategy/architecture input document, not a submission-ready standards-track draft.*
