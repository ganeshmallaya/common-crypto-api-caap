# Proposed Standard Framework

**Common Crypto API — framework specification, draft rev 02**

Status: working draft and strategy input. No standards body has adopted this.
Audience: PKI and certificate lifecycle vendors, HSM and KMS vendors, protocol implementers, standards reviewers.

---

## 1. Scope

This framework specifies a vendor-neutral API for cryptographic operations. The operations are signing, verification, key encapsulation, key derivation, and key wrapping. A calling application binds to none of these at compile time.

Algorithm selection happens at call time against an external policy. The API stays stable across the change from classical to post-quantum and hybrid algorithms, so one integration survives several algorithm generations.

This framework sits one layer above a hardware abstraction interface. PKCS#11 abstracts which token performs an operation. This framework abstracts which algorithm performs it.

---

## 2. Non-goals

The framework does not define new cryptographic algorithms.

It does not replace PKCS#11, TPM interfaces, or cloud KMS APIs. A provider may wrap any of them.

It does not define a user interface for any consuming product.

It does not, in this revision, mandate a single wire transport. It defines one normative binding in section 10 and states requirements for any additional binding.

---

## 3. Terminology

| Term | Definition |
|---|---|
| Operation | A cryptographic action a caller requests, independent of algorithm |
| Algorithm Identifier | A stable registered identifier for one algorithm or parameter set |
| Composite Identifier | An identifier for two or more algorithms combined, with a defined combiner |
| Policy Profile | A versioned machine-readable document that resolves an intent to an Algorithm Identifier |
| Intent | A named purpose a caller states, such as `tls-server-signing` |
| Provider | An implementation of the south contract that executes operations |
| Capability Descriptor | A machine-readable statement of what a Provider supports |
| Handle | An opaque reference to a key or credential |
| Conformance Level | A defined subset of this framework that an implementation claims |

---

## 4. Design principles

Six principles govern every other requirement.

1. **Operations, not algorithms.** Every call names an operation. The algorithm is always a resolved parameter and never a caller constant.
2. **Hybrid as a first-class case.** A Composite Identifier must dispatch to several primitives and a combiner without a special case at the call site.
3. **Policy separated from mechanism.** Resolution logic lives outside application code, in a versioned Policy Profile.
4. **Capability negotiation before execution.** A caller must be able to query what a Provider supports before it issues an operation.
5. **Opaque key material by default.** Keys are referenced by handle. Raw export requires a separate authorization.
6. **Fail closed on ambiguity.** If resolution is ambiguous or a capability is missing, the API returns an explicit error. Silent substitution is prohibited.

---

## 5. Object model

### 5.1 Algorithm Identifier

An Algorithm Identifier must be a stable string or integer registered in an external registry. It must not be a vendor-private value for any algorithm intended to work across implementations.

A Composite Identifier must declare its constituent identifiers and its combiner method explicitly. A naming convention is not a declaration.

### 5.2 Handle

A handle is an opaque reference. It must not expose backend structure such as an HSM slot identifier.

A handle must carry a creation time, its associated Algorithm Identifiers, and a lifecycle state of active, deprecated, or revoked.

### 5.3 Capability Descriptor

A Provider returns a descriptor on request. The descriptor must list supported operations, supported Algorithm and Composite Identifiers, whether execution is hardware-backed or software, and maximum key and message sizes.

### 5.4 Policy Profile

A Policy Profile maps an intent to a resolved Algorithm or Composite Identifier. It carries effective dates, expiry dates, and a deprecation state.

A profile must be versioned independently of the implementation. A policy update must not require a redeployment of the API.

---

## 6. Operations and conformance levels

![Conformance ladder](images/06-conformance-and-topologies-whiteboard.svg)

### 6.1 Level 0, mandatory

| Operation | Description |
|---|---|
| `GetCapabilities()` | Returns the Capability Descriptor for the calling context |
| `GenerateKeyPair(intent)` | Resolves the intent, generates a key pair, returns a handle |
| `Sign(handle, message)` | Signs with the algorithm bound to the handle |
| `Verify(handle_or_public_material, message, signature)` | Verifies a signature |
| `Encapsulate(handle)` | Performs KEM encapsulation, returns ciphertext and shared secret |
| `Decapsulate(handle, ciphertext)` | Performs KEM decapsulation |
| `ResolvePolicy(intent)` | Returns the identifier that would be used, without executing |

Level 0 also requires structured errors and prohibits silent algorithm substitution.

`ResolvePolicy` deserves a note. It exists so a build pipeline can assert what an environment will do before that environment does it. A dry run turns a policy change into something a test can catch.

### 6.2 Level 1, optional

Level 1 adds `DeriveSecret`, `Wrap`, and `Unwrap`. It requires support for at least one Composite Identifier with a registered combiner encoding. It requires live policy resolution rather than a static configuration file. It requires a `TransformKey` operation that changes the algorithm bound to a handle while the handle itself persists.

Level 1 is where agility becomes real. A Level 0 implementation abstracts the algorithm. A Level 1 implementation can change it.

### 6.3 Level 2, optional

Level 2 adds guarantees that a key cannot be extracted, attestation that a backend is FIPS-validated, a provider attestation format, and enforced provenance on policy profiles.

Regulated workloads need Level 2. Most workloads do not.

### 6.4 Compatibility rule

A consumer written against Level 0 must keep working against a Provider that offers Level 1 or Level 2. Levels add capability. They never change the meaning of a lower-level operation.

---

## 7. Bindings

### 7.1 Normative binding: RPC service

A conformant implementation must expose the operations in section 6 as an RPC service defined by a machine-readable interface definition. Protocol Buffers, OpenAPI, or an equivalent schema each satisfy this. The definition must be published with the specification rather than described in prose.

The interface definition is what prevents drift between vendors. A prose specification alone does not.

### 7.2 Optional binding: native library

An implementation may also expose a C ABI or a language-native binding for in-process use. A native binding must be semantically identical to the RPC binding. No capability may exist in one binding and not the other.

### 7.3 Compatibility binding: PKCS#11 shim

An implementation should provide a PKCS#11 provider module that presents the broker as a token. Applications that already speak PKCS#11 then reach the broker with no source change.

This binding does not offer every capability. A PKCS#11 caller cannot state an intent, so the shim maps a slot or a key label to an intent through configuration. Composite operations appear as a single mechanism. The mapping is a deliberate reduction, and it trades expressiveness for reach.

---

## 8. Error model

Errors must be structured. Each error carries a code, a machine-readable category, and a human-readable message. A free-text message alone is not sufficient.

The minimum categories are:

- `UNSUPPORTED_ALGORITHM`
- `POLICY_AMBIGUOUS`
- `POLICY_EXPIRED`
- `CAPABILITY_MISMATCH`
- `HANDLE_REVOKED`
- `PROVIDER_UNAVAILABLE`

Silent substitution of a default algorithm on error is prohibited by principle 6.

---

## 9. Algorithm identifier registry

The framework does not create a competing registry.

Identifiers should come from existing IANA registries wherever an equivalent exists. The IANA COSE Algorithms Registry is the primary source. Gaps should be filled through the standard IETF registration process.

Composite Identifiers need a registration entry that declares three things: the constituent identifiers, the combiner algorithm, and the byte-level encoding of the combined output.

The third item is the one that fails in practice. Two implementations can agree on the algorithms and still produce incompatible bytes. A registry entry that omits the encoding has not solved the interoperability problem.

---

## 10. Versioning and extensibility

The API version and the Policy Profile version are independent. Both appear explicitly in every request and response.

New operations and new Composite Identifiers must be addable without breaking an existing conformant client. Evolution within a major version is additive only.

A major version increase is required only for a breaking change to the operation semantics in section 6.

---

## 11. Security considerations

**Policy profile provenance.** A profile is a high-value target for tampering. Integrity and source authentication for the profile are mandatory. This revision states the requirement and does not yet specify the mechanism.

**Capability descriptor trust.** Do not use a Capability Descriptor for a security decision unless it arrived over an authenticated channel from the Provider.

**Downgrade resistance.** Resolution must be able to reject a request that would resolve to an algorithm weaker than the caller's stated minimum, even when a weaker algorithm is available.

**Centralization risk.** A central broker concentrates the consequence of a compromise. A deployment chooses between one auditable enforcement point and a smaller blast radius.

---

## 12. What a specification needs besides prose

A prose specification is necessary and not sufficient. Multi-vendor interoperability needs five artifacts alongside this document.

1. **A machine-readable interface definition.** Normative, versioned, and published in the same repository. This stops each vendor from interpreting request and response shapes independently.
2. **Test vectors.** Known-input and known-output pairs for every mandatory operation and for at least one Composite Identifier. An implementation can then be checked byte for byte rather than believed.
3. **A reference implementation.** One open-source Provider and one consumer client. This proves the specification is buildable as written. Ambiguities appear here instead of in the field.
4. **A conformance test suite.** A runnable suite any vendor executes against its own implementation to claim a Conformance Level.
5. **A certification program.** A later activity, governed separately, that gives enterprise buyers a signal beyond a vendor claim.

Without the first four, this document remains a design that vendors implement differently in the places that matter most. Those places are edge cases, error semantics, and composite encoding. Divergence there recreates the fragmentation the framework exists to remove.

---

## 13. Governance

The framework proposes a split across three bodies rather than one home.

**Algorithm identifiers** belong in the IANA and IETF registration process. No new registry.

**The specification, the interface definition, and the policy schema** belong to an open multi-vendor consortium. A Linux Foundation technical committee fits, because this material describes enterprise product shape rather than wire protocol.

**Conformance testing and certification** belong to a separately governed lab or a program adjacent to NCCoE. Independence from the specification authors is the point.

A single body for all three creates a conflict. The party that writes the specification should not also certify compliance with it.

---

## 14. Relationship to existing standards

| Standard | Relationship |
|---|---|
| NIST CSWP 39 | Source of the agility approach this framework implements |
| NIST IR 8547 | Supplies the deprecation and disallowance dates that force the timeline |
| FIPS 203, 204, 205 | Supply the post-quantum algorithms a Provider executes |
| RFC 7696 / BCP 201 | Covers agility at the protocol negotiation layer, below this framework |
| PKCS#11 v3.0 | A Provider may wrap it, and the shim in section 7.3 presents it upward |
| IANA COSE Algorithms | Primary source of Algorithm Identifiers |
| OASIS KMIP | Adjacent key management interoperability, complementary rather than overlapping |

---

## 15. Build sequence

Six steps, in this order. The order is the argument.

1. **Define both contracts as one machine-readable interface definition.** North and south in a single versioned schema. This artifact, not the prose, stops vendors diverging.
2. **Build a reference broker and one consumer binding.** This proves the specification is buildable. Open source from the first commit.
3. **Build two providers: liboqs and PKCS#11.** One software, one hardware. Enough to show a swap and to prove the south contract holds across very different backends.
4. **Build the PKCS#11 compatibility shim.** The shortest path to a demonstration against software that exists today.
5. **Build the composite path end to end.** ECDSA and ML-DSA through the orchestrator, resolved by a signed profile. Change the profile, get a different signature, change no code.
6. **Publish test vectors and a conformance suite.** This turns a design document into something a working group can adopt.

Steps 1 and 4 carry the argument. They answer the two questions every reviewer asks. The first question is how the design stops vendor drift. The second question is how it works with what an organization already runs.

---

## 16. Open issues

- The choice of interface definition language affects both bindings and the tooling ecosystem. Protocol Buffers, OpenAPI, and CDDL each have consequences.
- The policy profile signing mechanism is flagged and not designed.
- Whether Level 2 attestation reuses FIPS 140-3 language or needs a new format is unresolved.
- The compatibility story for a Level 0 consumer against a Provider that offers only Level 1 features needs a written rule.
- No latency measurement exists for a central broker on a hot signing path at enterprise volume.

---

*Continue to [use cases](03-use-cases.md).*
