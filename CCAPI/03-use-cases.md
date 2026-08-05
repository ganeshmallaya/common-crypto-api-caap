# Use Cases

**Common Crypto API — workload analysis, draft rev 02**

Eight workloads. Each entry states the current pattern, the call-site pressure, what breaks during a post-quantum change, what the API changes, the Conformance Level required, and what the API does not solve.

The last item in each entry matters most. An architecture that only lists wins is a sales document.

---

## How to read the call-site figures

The counts below are illustrative figures for a mid-size enterprise deployment. They are not measurements from a named organization. Any team can produce its own numbers with a repository search for algorithm constants, and that search is usually the first honest step in a migration.

---

## 1. Identity provider token signing

**Current pattern.** A token service names an algorithm in a JWS header constant. The value is `ES256` or `RS256`. Every issuance path repeats it.

**Call-site pressure.** High. Token issuance appears in access token paths, refresh paths, federation paths, device flows, and admin consoles. A mid-size platform holds 40 to 80 sites.

**What breaks.** ML-DSA-65 public keys are 1,952 bytes against 32 bytes for Ed25519. A JWKS document grows by roughly an order of magnitude. Header handling needs a composite algorithm value. Every relying party must verify the new algorithm before the issuer may use it.

**What the API changes.** The call becomes `Sign(handle, payload)`. The handle names an intent such as `idp-access-token`. A policy profile change moves the algorithm.

**Level required.** Level 1, for the composite identifier.

**What it does not solve.** Relying party coordination. The issuer cannot move until verifiers accept the new algorithm. The broker moves the cost to one place and does not remove it. Section 4 of the before-and-after document treats this as the governing constraint.

---

## 2. Service mesh and workload identity

**Current pattern.** A mesh issues short-lived X.509 certificates to workloads. The key type is fixed in the control plane configuration and often in a sidecar binary.

**Call-site pressure.** Low in application code and high in infrastructure configuration. The algorithm hides in Helm charts, mesh custom resources, and issuer templates rather than in source files.

**What breaks.** Certificate size grows. A handshake carrying a composite certificate chain may exceed a path MTU assumption. Short certificate lifetimes help, because a fleet rotates itself within hours.

**What the API changes.** The mesh certificate authority becomes a consumer. Key generation and signing route through the broker. The mesh stops holding an algorithm choice.

**Level required.** Level 1.

**What it does not solve.** Handshake size. A larger certificate is larger regardless of how the signature was produced. The API changes who chooses the algorithm and not what the algorithm costs on the wire.

**Why this case is the best first target.** Short certificate lifetimes make a mistake cheap. A bad policy change expires within hours instead of persisting for years. Any organization looking for a first production deployment should look here.

---

## 3. Internal certificate authority issuance

**Current pattern.** An internal certificate authority signs with a key created years ago. Issuance protocols include CMP, EST, and ACME. Profile templates name key types and signature algorithms.

**Call-site pressure.** Moderate in code and high in profile configuration.

**What breaks.** The certificate authority key itself. A root or intermediate signing key with a ten-year or twenty-year validity cannot simply change algorithm. It needs a new hierarchy, cross-signing, or a parallel chain. This is the hardest case in the list.

**What the API changes.** Issuance signing routes through the broker. The certificate authority gains a `TransformKey` path for subordinate keys. A composite chain becomes expressible without custom code.

**Level required.** Level 2, because a certificate authority key belongs in validated hardware.

**What it does not solve.** Trust store distribution. A new root must reach every trust store in the estate. That is a fleet management problem and no API touches it.

---

## 4. Build pipeline artifact and SBOM signing

**Current pattern.** A pipeline step signs a container image, a package, or a software bill of materials. The signing tool holds the algorithm.

**Call-site pressure.** Moderate. The pressure sits in pipeline definitions rather than in application source.

**What breaks.** Verification tooling on the consuming side. A signature format change reaches every verifier, and verifiers include air-gapped systems and customer environments.

**What the API changes.** The pipeline calls the broker. Signing keys live in an HSM through a provider rather than in a pipeline secret. Audit records show exactly which algorithm signed which artifact.

**Level required.** Level 1, with Level 2 where a release key requires hardware.

**What it does not solve.** Verifier reach. This case has the same asymmetry as case 1, with a longer tail, because customers control the verifiers.

---

## 5. Database field-level encryption

**Current pattern.** An application encrypts specific columns before it writes them. The cipher and mode appear in a data access layer. A data encryption key wraps under a key encryption key held in a KMS.

**Call-site pressure.** High, and concentrated. Most estates funnel field encryption through one data access layer, which makes this case unusually tractable.

**What breaks.** Less than expected. AES-256 remains acceptable under CNSA 2.0. The change lands on the wrapping key rather than on the data key. A KEM replaces a public-key wrap.

**What the API changes.** The wrap and unwrap operations route through the broker. A policy change moves the wrapping algorithm. Existing ciphertext stays readable, because the data encryption key did not change.

**Level required.** Level 1, for `Wrap` and `Unwrap`.

**What it does not solve.** Re-encryption of stored data, when policy does require it. Moving petabytes of ciphertext is an operations project. The broker makes the new writes correct and does not rewrite history.

**Why this case is attractive.** The concentration of call sites and the survival of AES-256 make it the cheapest real win in the list.

---

## 6. Records and archive signing

**Current pattern.** A records system signs documents for long-term retention. Retention periods run 7 to 30 years, and sometimes longer.

**Call-site pressure.** Low. Usually one signing service.

**What breaks.** The signature validity horizon. A signature created today with a classical algorithm must remain verifiable after that algorithm is broken. This is the archive problem and it is not the same as the transport problem.

**What the API changes.** Composite signatures become the default rather than a project. A policy profile records which algorithm signed which document, and the audit trail supports later re-validation.

**Level required.** Level 1.

**What it does not solve.** Signatures already in the archive. Those need re-signing or a timestamp-based preservation scheme. The API helps everything created after deployment.

---

## 7. Payment message authentication

**Current pattern.** A payment system computes a MAC over a message using a symmetric key in an HSM. The algorithm is fixed by a scheme specification.

**Call-site pressure.** Low in code and zero in choice. The scheme dictates the algorithm.

**What breaks.** Nothing soon. Symmetric MACs face no quantum threat comparable to public-key algorithms.

**What the API changes.** Little on the algorithm. Something on governance. The broker gives one audit point across a mixed HSM estate and one place to enforce a key ceremony policy.

**Level required.** Level 2.

**What it does not solve.** The scheme specification. When a card scheme mandates an algorithm, policy resolution has one legal answer. Agility has no meaning where an external body removes the choice.

**Why this case is included.** It shows the honest limit of the design. Some workloads do not need agility, and a framework should say which.

---

## 8. Device fleet firmware signing

**Current pattern.** A build server signs a firmware image. The device verifies the signature in a bootloader with a hardcoded public key and a hardcoded algorithm.

**Call-site pressure.** Low on the signing side and immovable on the verification side.

**What breaks.** The asymmetry. CNSA 2.0 expects exclusive post-quantum signing for software and firmware by 2030. Signing can change quickly. A deployed device cannot.

**What the API changes.** The signing side only. The build server becomes a consumer. It can produce a classical signature, a post-quantum signature, or both, driven by policy and matched to what a given fleet generation accepts.

**Level required.** Level 1 and Level 2, because a firmware signing key belongs in hardware.

**What it does not solve.** The bootloader. Verification sits outside the hard boundary described in section 7 of the architecture document. Agility arrives on the verification side only as the fleet turns over, which for medical and industrial equipment can take a decade.

**The useful reframing.** For this workload the API buys the ability to sign several ways at once from one pipeline. That is a different benefit from the other seven cases, and it is worth stating separately rather than blending into a single claim.

---

## Summary table

| Case | Call-site pressure | Level | Hardest remaining problem |
|---|---|---|---|
| Identity provider tokens | High | 1 | Relying party coordination |
| Service mesh identity | Low code, high config | 1 | Handshake size |
| Internal CA issuance | Moderate | 2 | Trust store distribution |
| Artifact and SBOM signing | Moderate | 1 and 2 | Verifier reach |
| Database field encryption | High, concentrated | 1 | Re-encryption of stored data |
| Records and archives | Low | 1 | Signatures already archived |
| Payment MAC | Low | 2 | Scheme removes the choice |
| Firmware signing | Low, asymmetric | 1 and 2 | Bootloader cannot change |

---

## Where to start

Two cases deserve a first deployment. Service mesh identity, because short certificate lifetimes make a mistake cheap. Database field encryption, because the call sites concentrate in one layer and AES-256 survives.

Two cases should wait. Internal certificate authority hierarchies, because a root key change is a program rather than a deployment. Firmware verification, because it sits outside the boundary.

---

*Continue to [the worked before-and-after example](04-before-and-after.md).*
