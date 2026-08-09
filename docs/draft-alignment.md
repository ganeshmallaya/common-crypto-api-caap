# Draft and architecture alignment review

Status: review record; no source file is promoted by this document

## Materials compared

This review compares:

- the historical root draft, `common-crypto-api-spec-draft-v0.1.md`;
- the untracked `CCAPI/` revision 02 architecture and `CCA-SPEC-1-v0.2.md`; and
- the current research authority in `docs/`, `schemas/`, and `examples/`.

The root draft and `CCAPI/` package remain inputs. The third group remains the
authoritative working research material under the repository rules.

## Alignment matrix

| Topic | Historical v0.1 | Proposed revision 02 | Current CAAP position |
| --- | --- | --- | --- |
| Core separation | Consumer API, policy engine, provider interface | Two contracts, broker, and control plane | Aligned: northbound Common Crypto API and southbound provider contract |
| Canonical name | Common Crypto API specification | Common Crypto API standard specification | Must be revised: CAAP is the research specification; Common Crypto API is its consumer interface |
| Status | Working draft, not standards-track | Architecture input, but repeatedly says standard and conformance | Keep exploratory language until a venue, normative scope, binding, and evidence exist |
| Algorithm choice | Resolved from policy; caller supplies intent | Caller cannot express an algorithm | Keep intent-first behavior, but allow explicit non-negotiable constraints and expected policy pins |
| Broker | Mostly implicit implementation layer | Router, resolver, composite orchestrator, handle manager, telemetry | Broker is an enforcement point; policy authority remains a separate decision point |
| Policy | Versioned intent-to-algorithm profile | Signed policy in a separate control plane | Aligned in direction; signing, trust, precedence, exception, rollback, and explanation semantics remain open |
| Provider | Software, HSM, KMS | Adds TPM, enclave, smartcard, compatibility shim | Extensible, but each provider class needs exact operation and assurance semantics |
| KMIP | Not named | Described only as adjacent | Promote to an explicit southbound adapter relationship; do not replace or relabel KMIP semantics |
| Key continuity | Opaque handle with algorithm metadata | Handle persists across provider and algorithm change | Narrow the claim: a logical reference may point to a successor key; mathematical cross-algorithm key conversion is not assumed |
| Combined cryptography | First-class composite identifier | Broker can split across providers and combine | Only for a separately defined construction, combiner, encoding, failure rule, and verified provider combination |
| PKCS#11 compatibility | Provider relationship | Shim can add adoption with no source change | Treat as a proposed reduced binding; intent and combined semantics may be lost and compatibility must be tested |
| Capability negotiation | Query before operation | Compared to TLS negotiation | Avoid the TLS analogy; capability discovery is scoped information, not agreement, authorization, or future availability |
| Certificate authority | Audience and possible consumer | CA use case and provider-adjacent workflow | CA or lifecycle workflow is a consumer/orchestrator; CAAP does not replace ACME, CMP, EST, issuance, revocation, or CLM |
| Conformance | Levels and future certification | Stronger levels and test claims | Premature until a normative binding, profiles, vectors, and implementation-independent suite exist |
| Deployment | RPC plus optional native | In-process, sidecar, central, tiered | Keep all as research topologies with different trust and availability assumptions |

## Concepts to incorporate

- The two-contract explanation is clearer than the original diagram.
- The explicit broker components help test implementation boundaries.
- The control plane should be kept off the hot path when authenticated cache
  and expiry rules allow it.
- The declared limits for constrained devices, boot-time verification, and
  line-rate data paths make the scope more credible.
- A compatibility adapter is valuable as an adoption experiment.
- Dry-run resolution, negative tests, and evidence are strong adoption hooks.
- KMIP should be a named provider-adapter target alongside PKCS#11.

## Claims to revise before promotion

1. **“The caller never states an algorithm.”** Prefer “the normal consumer
   contract expresses intent and constraints rather than selecting a provider
   algorithm.” Verification, protocol interoperability, and migration tooling
   may need explicit identifiers.
2. **“A new algorithm reaches production with no consumer code changes.”** Add
   “when the operation semantics, data shapes, protocol, verifier, provider,
   and deployment are compatible.”
3. **“A key changes algorithm under the same handle.”** Specify successor-key
   continuity. Do not imply private-key conversion or hide certificate and
   verifier consequences.
4. **“A key moves between providers.”** Make this conditional on custody,
   extractability, wrapping, attestation, and provider support.
5. **“The orchestrator combines classical and post-quantum operations.”** Do
   not define combination by dispatch. Require an externally or separately
   reviewed construction and byte-level encoding.
6. **“PKCS#11 applications need no source change.”** Treat this as a hypothesis
   for applications whose mechanism, handle, and operation semantics can be
   mapped without unsafe loss.
7. **“Level 2 is required for regulated workloads.”** Regulation and assurance
   requirements are context-specific. A CAAP level cannot make a generic
   regulatory claim.
8. **Quantitative migration, call-site, performance, and product claims.** Keep
   them out unless a primary source or reproducible measurement supports the
   exact claim.

## Relationship to current prior art

The June 2026 IBM preprints on application-level cryptographic agility describe
an orthogonal assessment model and an intent-based API with policy, stable key
identifiers, and key-evolution operations. CAAP should cite them and state the
remaining research question narrowly: whether an implementation-independent
broker and policy decision contract can connect enterprise governance to
heterogeneous provider protocols while preserving explicit failure and
evidence.

This is an overlap and differentiation claim for further research, not a claim
of novelty.

## Promotion decision

Do not replace the current `docs/` tree with `CCAPI/`. Promote reviewed concepts
individually, preserve unresolved issues, and update schemas, examples, and
tests together when the protocol shape changes.

## Sources

- [An Assessment Framework for Application-Level Cryptographic Agility](https://arxiv.org/abs/2606.13425)
- [Intent-Based Cryptographic API Design for Cryptographic Agility](https://arxiv.org/abs/2606.13445)
