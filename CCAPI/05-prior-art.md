# Prior Art

**Where this draft sits against the CCP Standard and the IBM Research papers**

---

## 1. Why this document exists

Three efforts reached the same conclusion within twelve months. None of them cites the others. A reader deserves to know which ideas are shared, which are borrowed, and which belong to this draft.

![Prior art positioning](images/07-prior-art-positioning-whiteboard.svg)

---

## 2. The three efforts

### 2.1 The CCP Standard

The Cryptographic Control Plane Standard appeared in May 2026 as version 0.9, licensed under CC BY 4.0. ANKATech Solutions publishes it, and that company sells a product it names as the reference implementation.

Its argument is that cryptography is the last infrastructure layer still living inside application code. It draws an analogy to networking and software-defined networking, and to secrets and secrets management. Applications reference a key identifier and an operation. The control plane resolves the rest.

It defines five pillars under the name CAPA, a six-level maturity model, five minimum capabilities, a four-layer reference architecture, and a four-phase migration program.

Two observations matter for a reader comparing it to this draft. Its GitHub repository holds documentation and no interface definition, no schema, and no reference code. It lists a standardized API specification as its own first open question, and states that it does not specify a wire protocol or API contract.

A third observation is smaller and worth noting. Its website and its repository README expand the CAPA acronym differently and present two different maturity scales.

### 2.2 The IBM Research papers

Two papers by Navaneeth Rameshan and Grégoire Messmer of IBM Research Europe, Zurich, appeared on arXiv on 11 June 2026 under CC BY 4.0.

The first paper, arXiv 2606.13425, builds an assessment framework. It decomposes cryptographic agility into seven orthogonal dimensions and scores each from 0 to 4. It then evaluates six real systems: PKCS#11, OpenSSL 3.0, JCA, Google Tink, AWS KMS, and HashiCorp Vault Transit. It reports three gaps that appear across all six. No system supports intent-based key creation. No system provides cryptographic governance as distinct from access control. No system offers algorithm transformation as an independent operation.

The second paper, arXiv 2606.13445, designs an API. It derives thirteen principles from five foundational properties, which are Abstraction, Stability, Temporal Flexibility, Separation, and Extensibility. It defines four abstractions that compose into a resolution chain of scope, policy, template, and provider. It specifies gRPC services with Protocol Buffers message types, including three key evolution operations named RotateKey, TransformKey, and MigrateKey. It closes with an ECDSA to ML-DSA migration walked through in five steps.

The second paper is the stronger technical contribution of the two. Its related work section says a complete agility stack needs two things. It needs a provider API and an orchestration layer above it. The papers address the first.

### 2.3 This draft

The Common Crypto API draft names two contracts, a north Consumer API and a south Provider SPI, with a broker between them. It defines five planes, a composite orchestrator, an opaque handle model, four deployment topologies, and three conformance levels. It requires a machine-readable interface definition as the normative binding and requires test vectors and a conformance suite as separate artifacts. It splits governance across three bodies. It states a hard boundary excluding constrained devices, boot-time roots of trust, and line-rate datapaths.

---

## 3. Where all three agree

The shared conclusion is that the algorithm name must leave the call site and that policy must resolve it externally. All three treat the post-quantum transition as the forcing event and treat hardcoded cryptography as the underlying condition.

All three separate a policy decision from a key management decision. All three treat provider substitution as a requirement rather than an optimization. All three published under CC BY 4.0 in 2026.

This convergence is useful evidence. Three independent efforts reaching one architecture suggests the architecture is correct rather than novel.

---

## 4. Where the three differ

| Dimension | CCP Standard | IBM papers | This draft |
|---|---|---|---|
| Primary layer | Enterprise control plane | Provider API | Both, with the seam named |
| Vocabulary | Key ID, abstraction layer, algorithm catalog | Scope, template, policy, provider | North contract, south contract, broker, handle |
| Intent expression | Narrative, no vocabulary defined | Scope enums per primitive | Named intent resolved by profile |
| Maturity model | Six linear levels | Rejects linear models for seven orthogonal dimensions | Three conformance levels, capability not maturity |
| Assessment method | Self-conformance against five capabilities | Falsifiable scoring of six real systems | Runnable conformance suite, proposed |
| Hybrid and composite | Mentions composite hybrids in a catalog | Not addressed as an operation | First-class operation with a registered combiner |
| Legacy compatibility | Not addressed | Not addressed | PKCS#11 shim as an adoption requirement |
| Interface definition | Named as open question 1 | Protocol Buffers patterns specified | Required as the normative binding |
| Test vectors | Absent | Absent | Required artifact |
| Stated boundary | Absent | Layer scope stated | Three excluded classes named explicitly |
| Governance | Single initiative, one vendor | Academic, no governance claim | Split across three bodies by design |

---

## 5. What this draft takes from the IBM papers

Two things, and the draft names them rather than absorbing them quietly.

**The assessment vocabulary is better than what this draft had.** The distinction between operation coupling and creation coupling is a real analytical improvement. The separation of access control authority from cryptographic selection authority is a distinction this draft should have drawn earlier and now does in section 3.5 of the architecture document.

**The three-operation key evolution model is right.** Rotation, algorithm transformation, and provider migration are genuinely different operations. This draft folds algorithm transformation into Conformance Level 1 and should credit the source of that clarity.

The draft does not adopt the scope enum vocabulary. That choice is deliberate. Scope enums per primitive give precise operational parameter grouping, and they also push a taxonomy decision into the wire format. This draft keeps a named intent string resolved by profile, which trades type safety for the ability to add an intent without a schema change. Reasonable people will disagree about that tradeoff, and a working group is the correct place to settle it.

---

## 6. What this draft claims as its own

Three contributions do not appear in either adjacent effort.

**Hybrid as a first-class operation.** The IBM design specifies key evolution but does not treat one signature spanning two primitives as an operation. CCP lists composite algorithms in a catalog without an operational model. The composite orchestrator in section 4 of the architecture document dispatches constituent primitives to different backends, applies a registered combiner, and returns one result. The specific mechanism is the split of one signature across a validated HSM and a software provider. That split solves a real sequencing problem, because HSM firmware for a new algorithm arrives late.

**A compatibility path for cryptography already in production.** Neither adjacent effort addresses the software that exists today. Most production cryptography reaches hardware through PKCS#11. A shim that presents the broker as a PKCS#11 token brings that software in with no source change. This is the difference between an architecture a working group discusses and an architecture an enterprise can pilot next quarter.

**A stated boundary and a conformance program.** The IBM papers scope themselves to a layer. CCP claims broad applicability. This draft names three classes of system it cannot serve and gives its reasons. It then requires test vectors and a runnable conformance suite, and it separates the certifying body from the authoring body. A specification that cannot be tested is a design document, and a specification certified by its own authors is a marketing claim.

---

## 7. Where all three fall short

Honesty about the shared gaps is more useful than a comparison table.

**Nobody has measured anything.** No published latency figure exists for a broker on a hot signing path at enterprise volume. No developer study tests whether an intent-based API actually reduces error rates. The IBM papers explicitly leave policy evaluation scalability unquantified. This draft has the same gap and cannot claim otherwise.

**Nobody has proven substitution safety.** All three assert that grouping algorithms behind an intent permits safe substitution. None offers a formal argument or a machine-checked proof that a substitution preserves the security property the caller needed.

**Nobody handles the protocol layer.** All three address application and data-at-rest cryptography. None reconciles this model with TLS cipher suite negotiation, and RFC 7696 covers that ground separately. A complete story needs both, and no effort has written it.

**Nobody closes the automation loop.** All three describe policy-driven selection. None builds and evaluates a loop that runs discovery, updates policy, and executes transformation without a human in the middle. The IBM assessment framework names this as its top rung and does not reach it.

---

## 8. What this means for the reader

CCP is the same idea at a higher layer, without an API. The IBM papers are a stronger API design without hybrid operations, without a legacy path, and without a conformance program. This draft occupies the seam between them and adds the two pieces neither has.

That position is defensible and it is not a claim of priority. Three efforts arrived at one architecture independently. The useful question is no longer whether the architecture is right. The useful question is who builds the interface definition, the test vectors, and the shim, because those artifacts decide whether any of this reaches production.

---

## 9. Sources

- CCP Standard, version 0.9 working draft, https://ccp-standard.org and https://github.com/ccp-standard/standard
- Rameshan, N. and Messmer, G. *An Assessment Framework for Application-Level Cryptographic Agility.* arXiv 2606.13425
- Rameshan, N. and Messmer, G. *Intent-Based Cryptographic API Design for Cryptographic Agility.* arXiv 2606.13445
- Housley, R. *Guidelines for Cryptographic Algorithm Agility.* RFC 7696, BCP 201
- NIST IR 8547 initial public draft, *Transition to Post-Quantum Cryptography Standards*
- NIST CSWP 39, *Considerations for Achieving Crypto Agility*
- Lazar, D. et al. *Why does cryptographic software fail?* APSys 2014. The finding that 83 percent of 269 cryptographic CVEs came from API misuse rather than primitive implementation flaws.

---

*Return to the [index](README.md).*
