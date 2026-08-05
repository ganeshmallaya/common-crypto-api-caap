# Common Crypto API: Standard Specification

**Document:** CCA-SPEC-1
**Version:** 0.2, working draft
**Date:** August 2026
**Author:** Ganesh Mallaya
**License:** CC BY 4.0
**Status:** Architecture input. No standards body has adopted this document.

---

## Preamble

This is the single specification document. It replaces the separate architecture and framework drafts, and it carries no code samples on purpose. A specification that leans on one language teaches readers to think in that language.

---

## 1. Definition

A **Common Crypto API** is a two-contract interface that separates the cryptographic operation a caller needs from the algorithm that satisfies it.

A caller states an operation and a handle. The caller never states an algorithm. A broker resolves the algorithm from signed policy at call time. A provider then executes the operation on a backend the caller never names.

Two properties define conformance. The caller cannot express an algorithm, and the algorithm can change without the caller changing.

### 1.1 The two contracts

**The north contract** faces callers. It carries operations only. It stays additive within a major version, so a caller written today keeps working when the contract grows.

**The south contract** faces backends. Any software library, network HSM, cloud KMS, TPM, secure enclave, or smartcard that satisfies it registers as a provider.

Neither contract references the other. That absence is the design.

### 1.2 What sits between them

A **broker** routes operations to providers, resolves intent against policy, orchestrates composite operations, issues opaque handles, and records what resolved.

A **control plane** governs the broker from outside the request path. It holds versioned policy profiles, an algorithm identifier registry, a cryptographic inventory, and a signed distribution path for profiles.

---

## 2. The structural problem

Cryptographic migration cost does not track cryptographic difficulty. It tracks the number of source locations where a person typed an algorithm name.

The SHA-1 transition proves the point. Replacing SHA-1 with SHA-256 needed no new interface and no new key format. The change still took roughly a decade. Microsoft stopped delivering updates to devices without SHA-2 support in August 2019, more than two years after the SHAttered collision in February 2017.

Nothing about SHA-256 was hard. The count was hard.

Post-quantum algorithms make the count worse, because they change key sizes and signature sizes as well as names. An ML-DSA-65 public key is 1,952 bytes. An Ed25519 public key is 32 bytes. Code that assumed a size now fails alongside code that assumed a name.

### 2.1 The recurrence problem

One migration is a project. Repeated migrations are a condition.

NIST IR 8547 proposes deprecation of 112-bit public-key algorithms after 2030 and disallowance after 2035. Parameter sets will keep moving after that date. An organization that treats the transition as a single event will pay the same cost again for every later revision.

This specification therefore optimizes for the second migration rather than the first. That choice governs every requirement below.

---

## 3. The architectural precedent

Certificate renewal made this exact transition, and recently enough that the people who lived through it are still working.

**Before.** An engineer generated a certificate signing request by hand. The expiry date lived in a spreadsheet or in nobody's memory. Renewal was a ticket. An outage was the notification mechanism. Every team held its own procedure, and no central system knew what existed.

**After.** ACME and certificate lifecycle platforms moved the decision out of the procedure. An application requests a certificate for an identity. Infrastructure decides the validity period, the issuing authority, and the renewal schedule. Policy changes reach every certificate without a single team changing a runbook.

The certificate did not become simpler. The decision moved.

Cryptographic algorithm selection now sits where certificate renewal sat in 2015. The decision lives in the wrong layer, nobody has a reliable inventory, and the cost of change scales with the number of teams rather than the difficulty of the change.

---

## 4. The six pillars

These pillars are engineering properties, not organizational postures. Each one is testable against an implementation.

### Pillar 1: Contract stability

The north contract changes only by addition within a major version. A caller written against an earlier revision keeps working against a later one.

*Test:* Compile a caller from the earliest published revision against the current contract. It must build and run.

### Pillar 2: Intent resolution

Algorithm selection happens outside caller code, in a versioned and signed policy profile, and it happens at call time rather than at build time.

*Test:* Change a profile. Observe a different algorithm in the audit record. Confirm that no artifact was rebuilt.

### Pillar 3: Composite equivalence

A hybrid operation is one operation. A composite identifier dispatches to several primitives, possibly across different backends, and a registered combiner produces a single result. The call site never learns that the operation was composite.

*Test:* Compare a caller invoking a single-algorithm handle against the same caller invoking a composite handle. The call must be byte-identical.

### Pillar 4: Provider substitutability

A key moves between backends without a change to its handle or to caller code.

*Test:* Migrate a key from a software provider to a hardware provider. The handle must remain valid and the caller must remain unmodified.

### Pillar 5: Verifiable conformance

Conformance is a claim an independent party can check. This requires a machine-readable interface definition, published test vectors, and a runnable suite. The body that certifies must not be the body that authors.

*Test:* A third party runs the suite against an implementation and reproduces the published result.

### Pillar 6: Declared boundary

The specification names the systems it cannot serve, and it gives reasons.

*Test:* Read section 8. A reviewer must be able to argue with the boundary rather than discover it.

The sixth pillar is unusual and deliberate. A specification that claims universal reach invites a reviewer to find the case it fails. A specification that draws its own boundary invites a reviewer to argue about where the boundary sits, which is the more useful conversation.

---

## 5. The call-site maturity model

Existing maturity models measure organizational capability. This one measures a single physical fact: where the algorithm decision lives. That fact is observable, so each level carries a test an engineer can run this week.

### CS0: In the source

The algorithm name appears as a constant in application source. Change requires an edit, a build, a review, and a deployment for every affected service.

*How to test:* Search the repository for algorithm names. A non-zero count places the system here.
*Post-quantum exposure:* Critical. The algorithm is as immovable as any other compiled constant.

### CS1: In configuration

The algorithm name has moved to a configuration file or an environment variable. Change requires a restart rather than a build.

*How to test:* Change the configuration value. If the service accepts the new algorithm after a restart and without a rebuild, the system reached CS1.
*Post-quantum exposure:* High. Configuration is still per-service, so the count problem remains.

Most organizations that describe themselves as agile sit here. CS1 removes the compiler from the path and leaves the coordination cost intact.

### CS2: On the handle

The algorithm binds to the key rather than to the call. Caller code dispatches on the handle and names nothing.

*How to test:* Issue two handles bound to different algorithms. Pass each to the same unchanged call path. Both must succeed.
*Post-quantum exposure:* Medium. New keys can adopt a new algorithm. Existing keys cannot change.

### CS3: In signed policy

A policy profile external to every service resolves intent to an algorithm at call time. The profile is versioned and signed, and resolution rejects any result below the caller's stated minimum strength.

*How to test:* Publish a new signed profile. Confirm the change reaches every consumer without a restart. Then publish a profile that selects a weaker algorithm and confirm that resolution refuses it.
*Post-quantum exposure:* Low. New operations follow policy immediately across the estate.

### CS4: Transformable under a stable handle

An existing key changes algorithm while its handle persists. Stored references stay valid. Composite operations are available, and the combiner encoding comes from a registry rather than from local convention.

*How to test:* Transform a live key to a different algorithm. Confirm that a reference stored before the transformation still resolves.
*Post-quantum exposure:* Minimal. Both new and existing keys move by policy.

### Why the ladder stops at five

CS4 is the last level a specification can define, because a higher level describes automation rather than interface capability. A system that discovers its own exposure, updates policy, and executes transformation without a human belongs to an orchestration layer above this contract. That layer deserves its own specification and this document does not claim it.

---

## 6. Operations and conformance levels

### 6.1 Level 0, mandatory

Capability query. Key pair generation from an intent. Signing. Verification. Key encapsulation and decapsulation. Policy resolution as a dry run that returns the identifier without executing.

Level 0 also requires structured errors and prohibits silent algorithm substitution.

The dry run earns its place in the mandatory set. It lets a build pipeline assert what an environment will do before that environment does it, which turns a policy change into something a test catches.

### 6.2 Level 1, optional

Secret derivation, key wrapping, and key unwrapping. At least one composite identifier with a registered combiner encoding. Live policy resolution rather than a static file. Algorithm transformation on an existing handle.

Level 0 abstracts the algorithm. Level 1 changes it. Only Level 1 satisfies CS4.

### 6.3 Level 2, optional

Guarantees that a key cannot be extracted. Attestation that a backend holds a current validation. A defined provider attestation format. Enforced provenance on policy profiles.

Regulated workloads need Level 2. Most workloads do not.

### 6.4 Compatibility rule

A caller written against Level 0 must keep working against a provider offering Level 1 or Level 2. Levels add capability and never change the meaning of a lower-level operation.

---

## 7. Required artifacts

A prose specification is necessary and not sufficient. Five artifacts must accompany this document.

1. **A machine-readable interface definition** covering both contracts in one versioned schema. This artifact, and not the prose, prevents divergence between vendors.
2. **Test vectors** for every mandatory operation and for at least one composite identifier, so an implementation can be checked rather than believed.
3. **A reference implementation** of one provider and one caller, published openly. Ambiguities surface here instead of in production.
4. **A conformance suite** any vendor runs to claim a level.
5. **A certification program** governed separately from the authors.

Without the first four this document remains a design that vendors implement differently in the places that matter most. Those places are error semantics, edge cases, and composite encoding. Divergence there recreates the fragmentation the specification exists to remove.

---

## 8. Declared boundary

Three classes of system sit outside this specification.

**Constrained devices.** A microcontroller with 32 KB of memory cannot host a broker or reach a policy service. Its algorithm is fixed when the image is built.

**Boot-time roots of trust.** A measured boot sequence verifies a signature before a network stack exists. It has nothing to ask.

**Line-rate datapaths.** A datapath encrypting frames at line rate cannot afford a broker hop per frame.

This is a datacenter and enterprise-workload specification. It is not a universal one.

One asymmetry deserves attention. Firmware signing happens on a build server, which is an ordinary workload and fully in scope. Firmware verification happens on the device, which is out of scope. The signing side gains agility immediately. The verification side gains it only as the fleet turns over, and for medical or industrial equipment that takes a decade.

---

## 9. What this specification does not solve

**Verifier coordination.** A signer cannot produce a signature nobody accepts. Verifiers gain capability first, then policy switches the signer. This specification gives the signer one switch and gives the verifiers nothing.

**Artifact size.** A larger post-quantum key is larger. The specification changes who selects the algorithm, not what the algorithm costs on the wire.

**Stored data.** Where policy requires re-encryption, moving existing data is an operations program. The specification makes new operations correct and does not rewrite history.

**Externally mandated algorithms.** Where a payment scheme or a regulator fixes the algorithm, resolution has one legal answer. Agility has no meaning where an outside body removes the choice.

**Latency.** No published measurement exists for a broker on a hot signing path at enterprise volume. This gap is the strongest argument for building the reference implementation before promising a number.

---

## 10. Security considerations

**Policy profile provenance.** The profile is the highest-value target in the design. An attacker who edits a profile does not need to break an algorithm, because the attacker can select a weaker one instead. Profiles are signed at source and verified before use. This revision states the requirement and does not yet specify the mechanism.

**Downgrade resistance.** A caller states a minimum strength. Resolution must reject any result below that floor, even when a weaker algorithm is available and would work.

**Failure behavior.** The broker fails closed. Ambiguous resolution, a missing capability, or an expired profile each produce an explicit error. Silent substitution produces a system that looks healthy while it signs with an algorithm nobody approved, and that failure surfaces during an audit two years later with keys already in the field.

**Capability descriptors.** Do not use a descriptor for a security decision unless it arrived over an authenticated channel.

**Centralization.** A central broker concentrates the consequence of a compromise. A deployment chooses between one auditable enforcement point and a smaller blast radius. The specification does not pretend the tradeoff disappears.

**Audit as evidence.** The audit record is strong for compliance and weak as forensic proof, because an attacker controlling the broker also controls the record.

---

## 11. Governance

Three functions belong to three bodies.

**Algorithm identifiers** belong in the IANA and IETF registration process. No new registry.

**The specification, the interface definition, and the policy schema** belong to an open multi-vendor consortium, because this material describes enterprise product shape rather than wire protocol.

**Conformance testing and certification** belong to an independently governed program.

A single body for all three creates a conflict. The party writing a specification should not certify compliance with it.

---

## 12. Relationship to existing standards

| Standard | Relationship |
|---|---|
| NIST CSWP 39 | Source of the agility approach this specification implements |
| NIST IR 8547 | Supplies the 2030 and 2035 dates that force the timeline |
| FIPS 203, 204, 205 | Supply the post-quantum algorithms a provider executes |
| RFC 7696 / BCP 201 | Covers agility at protocol negotiation, one layer below |
| PKCS#11 v3.0 | A provider may wrap it. A compatibility module may present the broker as a token. |
| IANA COSE Algorithms | Primary source of algorithm identifiers |
| OASIS KMIP | Adjacent key management interoperability, complementary |

---

## 13. Open questions

1. Which interface definition language. The choice affects bindings and the whole tooling ecosystem.
2. The policy profile signing mechanism. The requirement exists and the format does not.
3. Which registry holds composite encodings. Two implementations can agree on algorithms and still produce incompatible bytes.
4. Whether Level 2 attestation reuses existing validation language or needs a new format.
5. Latency under a central deployment on a hot path at enterprise volume.

---

## 14. Build sequence

1. Publish both contracts as one machine-readable interface definition.
2. Build a reference broker and one caller binding, openly, from the first commit.
3. Build two providers, one software and one hardware, to prove the south contract holds across very different backends.
4. Build a compatibility module for existing interfaces, so software that exists today can participate without a source change.
5. Build the composite path end to end, driven by a signed profile.
6. Publish test vectors and a conformance suite.

Steps 1 and 4 carry the argument. They answer the two questions every reviewer asks. The first is how the design prevents vendor divergence. The second is how it works with what an organization already runs.

---

## 15. Citation

Mallaya, G. (2026). *Common Crypto API: Standard Specification.* CCA-SPEC-1, version 0.2. https://ganeshmallaya.com/research/common-crypto-api

---

*#GMBlogs*
