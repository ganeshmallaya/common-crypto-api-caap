# Common Crypto API

**A vendor-neutral cryptographic operation API for the post-quantum transition.**

Status: architecture input, draft rev 02. Not a submission to any standards body.
Author: Ganesh Mallaya.
Last revised: August 2026.

---

## The claim in four sentences

Applications name the algorithm at the call site. That single habit turns every future algorithm change into a code change. The Common Crypto API removes the algorithm name from the call and resolves it from signed policy instead. One integration then survives several algorithm generations.

![The problem](images/01-the-problem-whiteboard.svg)

---

## Why this draft exists

Two things happened in 2024 and 2026. NIST published FIPS 203, FIPS 204, and FIPS 205 in August 2024. NIST IR 8547 then proposed to deprecate 112-bit public-key algorithms after 2030 and to disallow them after 2035. Every enterprise now faces a forced algorithm change on a published clock.

The clock is the easy part. The hard part is that most organizations do not know how many places their code names an algorithm. The migration cost tracks that count, not the difficulty of the new algorithm.

This research set describes an architecture that moves the cost once and then keeps it near zero.

---

## Read in this order

| File | What it covers |
|---|---|
| [01-architecture.md](01-architecture.md) | The five planes, the two contracts, the broker, and the parts this design refuses to cover |
| [02-standard-framework.md](02-standard-framework.md) | Terminology, object model, operations, conformance levels, bindings, governance split |
| [03-use-cases.md](03-use-cases.md) | Eight concrete workloads, with call-site counts and honest limits per case |
| [04-before-and-after.md](04-before-and-after.md) | One worked migration in code: access token signing from ES256 to a hybrid signature |
| [05-prior-art.md](05-prior-art.md) | How this compares to the CCP Standard and to the two IBM Research papers |
| [06-seo-and-metadata.md](06-seo-and-metadata.md) | Titles, meta tags, schema, and image briefs for publication |

---

## The architecture in one image

![Reference architecture](images/03-reference-architecture-whiteboard.svg)

---

## What is different about this draft

Three things do not appear in the adjacent work. Each one is a design decision, not a feature list.

1. **Hybrid signatures are a first-class operation.** One composite identifier dispatches to several primitives across different backends. A registered combiner then produces a single result. The call site never learns that the operation was hybrid.
2. **A PKCS#11 compatibility shim carries existing code.** Applications that already speak PKCS#11 connect without a code change. This is the shortest path from a design document to a running demonstration.
3. **The draft names its own boundary.** A 32 KB microcontroller cannot host a broker. A measured boot root cannot call a policy service. Those algorithms stay fixed at build time, and the draft says so rather than claiming universal reach.

---

## What this draft does not claim

It does not define new algorithms. It does not replace PKCS#11, TPM interfaces, or cloud KMS APIs. It does not remove the work of coordinating verifiers during a signature migration. It moves that work to one place and makes it repeatable.

---

## Citation

Mallaya, G. (2026). *Common Crypto API: a vendor-neutral cryptographic operation API for the post-quantum transition.* Draft rev 02. https://ganeshmallaya.com/research/common-crypto-api

## References

- NIST CSWP 39, *Considerations for Achieving Crypto Agility*
- NIST IR 8547 (initial public draft), *Transition to Post-Quantum Cryptography Standards*
- FIPS 203 (ML-KEM), FIPS 204 (ML-DSA), FIPS 205 (SLH-DSA)
- RFC 7696 / BCP 201, *Guidelines for Cryptographic Algorithm Agility*
- IANA COSE Algorithms Registry
- PKCS#11 v3.0, OASIS Cryptographic Token Interface
