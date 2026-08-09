# Architecture

**Common Crypto API — reference architecture, draft rev 02**

---

## 1. The problem, stated exactly

A developer writes one line to sign a token. That line names a curve, a hash, a padding scheme, an encoding, and a library. Five cryptographic decisions enter the source tree at one point. The compiler then locks them.

Multiply that by every service in an estate. A mid-size identity platform holds tens of such lines. A large enterprise holds tens of thousands across its whole portfolio. Nobody has an accurate count, because no build system reports it.

The migration cost follows the count. It does not follow the algorithm. Replacing SHA-1 with SHA-256 required no new interface, and it still took the industry roughly ten years. Microsoft stopped shipping updates to devices without SHA-2 support in August 2019, more than two years after the SHAttered collision in February 2017.

This tells us the useful thing. The obstacle is not cryptographic difficulty. The obstacle is the number of places a human typed a name.

---

## 2. The thesis: two contracts and one broker

![Two contracts](images/02-two-contracts-whiteboard.svg)

The design rests on two stable interfaces and one component between them.

**The north contract** is the Consumer API. Applications call it. It names operations only. It never names an algorithm.

**The south contract** is the Provider SPI. Backends implement it. A software library, a network HSM, a cloud KMS, a TPM, or an enclave each satisfies the same contract.

**The broker** sits between them. It routes an operation to a provider. It resolves intent to a concrete algorithm. It orchestrates hybrid operations. It records what resolved.

Consumers depend on the north contract alone. Backends satisfy the south contract alone. Neither side holds a reference to the other. A new algorithm, a new appliance, or a policy change reaches production through the broker, and no consumer code changes.

That property is the whole design. Everything below is a consequence of it.

---

## 3. The five planes

![Reference architecture](images/03-reference-architecture-whiteboard.svg)

### 3.1 Consumer plane

These systems produce cryptographic intent. They include identity providers, service mesh workloads, PKI and certificate authority services, SSH certificate authorities, build and release pipelines, databases and object storage, JOSE and COSE token handling, device onboarding services, and industrial control identities.

Two consumers sit at the edge of this plane and only partly belong to it. Secure boot and firmware verification fix their algorithm at build time. Section 7 explains why the draft excludes them rather than pretending otherwise.

### 3.2 Interface layer

The north contract needs bindings. Four exist.

1. A native SDK for in-process use, with low latency and no network hop.
2. A gRPC service for a shared or per-cluster deployment.
3. A sidecar agent for one pod or one host.
4. A PKCS#11 compatibility shim for applications that already speak PKCS#11.

The fourth binding matters more than its position suggests. Most cryptography in production today reaches hardware through PKCS#11. A shim that presents the broker as a PKCS#11 token brings those applications in with no source change. Section 5 of the framework document treats this as an adoption requirement rather than a convenience.

Capability negotiation happens in this layer. A consumer calls `GetCapabilities()` before it commits to an operation. This works the way a TLS handshake negotiates a cipher suite. A caller never assumes support that a provider lacks.

### 3.3 Broker core

Five components, and only this plane holds state on the hot path.

**Operation router.** Maps an operation and a handle to a provider.

**Composite orchestrator.** Handles hybrid identifiers. Section 4 covers it separately, because it is the largest departure from existing interfaces.

**Policy resolver client.** Turns an intent into a concrete algorithm identifier by reading the active profile.

**Handle manager.** Issues and tracks opaque key references. A handle never exposes an HSM slot number or any other backend structure.

**Audit and telemetry.** Records what resolved for each operation. This record is the input to a cryptographic bill of materials, and it arrives as a by-product rather than as a separate discovery project.

### 3.4 Provider plane

Software providers include liboqs, an OpenSSL 3.x provider bridge, BoringSSL or Rust stacks, and a pure software fallback. Hardware providers include network HSMs through PKCS#11, cloud KMS services, TPM 2.0, secure enclaves, smartcards, and a bridge for quantum random number generators.

The software fallback earns its place. HSM firmware for a new algorithm often arrives months or years after the standard. A software provider lets policy move first, with the hardware provider taking over when it becomes available. The consumer sees neither event.

### 3.5 Control plane

Four components govern what the broker resolves to. These sit off the hot path wherever the deployment allows it.

**Policy and agility engine.** Holds versioned profiles and deprecation states.

**Algorithm identifier registry.** Draws identifiers from IANA registries and adds composite entries.

**Crypto inventory.** The system of record for keys, algorithms, and their locations.

**Signed profile distribution.** Provides provenance and defends against downgrade.

The fourth item carries the highest risk in the whole design. An unsigned policy profile is a single point of downgrade for every consumer at once. An attacker who edits a profile does not need to break an algorithm. The attacker simply selects a weaker one. Profiles are therefore signed at source and verified before use.

Resolution also enforces a floor. A caller states a minimum strength. Resolution rejects any result below that floor, even when a weaker algorithm is available and would technically work.

---

## 4. The composite orchestrator

![Composite orchestrator](images/05-composite-orchestrator-whiteboard.svg)

Hybrid cryptography is the reason this component exists.

During a transition an organization needs both a classical and a post-quantum primitive in one signature. The classical part satisfies a validated hardware requirement. The post-quantum part defends against a future attack. Neither alone is enough.

Existing interfaces express this badly. PKCS#11 has no concept of one operation that spans two mechanisms. An application therefore calls twice, combines the results itself, and encodes the combination by local convention. Every application then invents a slightly different encoding, and interoperability fails at exactly the point where it matters.

The orchestrator removes that from the call site. One composite identifier arrives. The orchestrator reads the constituent identifiers and the combiner from the registry. It dispatches each primitive to a provider that supports it, and those providers may differ. It applies the registered combiner. It returns one result.

The dispatch across different backends is the useful detail. An ECDSA operation can execute on a FIPS-validated HSM while the ML-DSA operation executes in software on the same host. The organization gets a hybrid signature without waiting for HSM firmware. The caller learns none of this.

Two properties follow. Hybrid stops being a special case bolted onto application code. The byte encoding of a composite result becomes a registry entry rather than a local decision.

---

## 5. The handle model

Keys are referenced, never handled.

A handle is opaque. It carries a creation time, the algorithm identifiers bound to it, and a lifecycle state of active, deprecated, or revoked. It does not carry a slot identifier, a file path, a key URI, or any other backend detail.

This constraint does real work. A key can move from a software provider to an HSM, and the handle does not change. An algorithm can change under the handle through an explicit transform operation, and the calling code does not change. Applications that store a handle in a database keep working across both events.

Raw key export exists, and it requires a separate authorization. It is never a side effect of another call.

---

## 6. Deployment topologies

![Conformance and topologies](images/06-conformance-and-topologies-whiteboard.svg)

The same two contracts support four placements.

**Topology A, in-process library.** The broker links into the application. Lowest latency and no network hop. Fits latency-critical single-tenant services and code that sits next to an HSM.

**Topology B, sidecar or local daemon.** The broker runs as a per-pod or per-host agent. Applications call over a local socket. Fits Kubernetes, service mesh deployments, and estates with many languages.

**Topology C, central service.** The broker runs as a networked service with high availability. Policy enforcement and audit collect in one place. Fits enterprise-wide governance and shared HSM pools.

**Topology D, tiered.** A local broker handles hot operations. A central service holds policy and inventory and synchronizes to the local brokers. This is the realistic production default at scale.

The topology changes latency and blast radius. It never changes the call.

---

## 7. The hard boundary

Three classes of system sit outside this architecture, and the draft states that plainly.

**Constrained devices.** A microcontroller with 32 KB of memory cannot host a broker or reach a policy service. Its algorithm is fixed when the image is built.

**Boot-time roots of trust.** A measured boot sequence verifies a signature before any network stack exists. It cannot ask a policy engine anything.

**Line-rate datapaths.** A MACsec or IPsec datapath running at line rate cannot afford a broker hop per frame.

This is a datacenter and enterprise-workload architecture. It is not a universal one.

Naming the limit is a design choice with a purpose. A specification that claims to cover every case invites a reviewer to find the case it fails. A specification that draws its own boundary invites a reviewer to argue about where the boundary sits, which is a more useful conversation.

One nuance deserves attention. Firmware **signing** happens on a build server, which is an ordinary workload and fully inside this architecture. Firmware **verification** happens on the device, which is outside it. The signing side gains agility. The verification side gains agility only when the device fleet turns over. Section 3 of the use-case document treats this asymmetry as the governing constraint for device workloads.

---

## 8. Failure behavior

The broker fails closed.

If policy resolution produces an ambiguous result, the API returns an error. If a required capability is absent, the API returns an error. If a profile has expired, the API returns an error. The broker never selects a default algorithm quietly.

This rule exists because the alternative is worse than an outage. A silent substitution produces a system that appears healthy while it signs with an algorithm nobody approved. An error stops a deployment. A silent substitution stops an audit, two years later, after the keys are in the field.

Errors are structured. Each carries a code, a machine-readable category, and a human-readable message. The minimum categories are `UNSUPPORTED_ALGORITHM`, `POLICY_AMBIGUOUS`, `POLICY_EXPIRED`, `CAPABILITY_MISMATCH`, `HANDLE_REVOKED`, and `PROVIDER_UNAVAILABLE`.

---

## 9. Security considerations

**Profile integrity.** Covered in section 3.5. The policy profile is the highest-value target in the design, and provenance is mandatory rather than advisory.

**Capability descriptors.** A descriptor arrives from a provider. Do not use it for a security decision unless it arrived over an authenticated channel.

**Downgrade resistance.** Resolution must be able to reject a request that would produce an algorithm weaker than the caller's stated minimum.

**Broker as a target.** Centralizing cryptographic operations centralizes the consequence of a compromise. Topology C concentrates this risk, and Topology A distributes it. A deployment chooses between one auditable point and a smaller blast radius. The draft does not pretend that this tradeoff disappears.

**Audit trail as evidence.** The audit record states which algorithm executed for which operation. If an attacker controls the broker, the attacker controls the record. The audit trail is therefore useful for compliance and weak as a forensic control against a broker compromise.

---

## 10. Open questions in the architecture

Four items remain undecided, and the draft flags them rather than hiding them.

1. **Policy profile signing mechanism.** The requirement exists. The format does not.
2. **Composite encoding authority.** Registry entries must fix byte-level encoding. Which registry holds them is unresolved. Section 9 of the framework document covers the options.
3. **Provider attestation format.** Conformance Level 2 requires attestation. Whether it reuses FIPS 140-3 language or needs a new format is open.
4. **Latency budget under Topology C.** No published measurement exists for a broker on a hot signing path at enterprise volume. This gap is the strongest argument for building the reference implementation early.

---

*Continue to [the proposed standard framework](02-standard-framework.md).*
