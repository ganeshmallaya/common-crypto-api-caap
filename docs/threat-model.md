# Threat model

Status: initial research threat model

## Scope

This model covers the CAAP consumer, broker, policy path, provider adapter,
cryptographic backend, and research-site publication boundary. It does not prove
that a particular deployment is secure.

## Protected assets

- Private keys and derived secrets
- Authorization and caller identity
- Policy profiles, lifecycle state, and provenance
- Algorithm and provider resolution decisions
- Key references and their tenant binding
- Capability descriptors
- Operation inputs and outputs
- Audit records and correlation identifiers
- Reviewed public content and its source-commit provenance

## Relevant adversaries

- An unauthenticated network attacker
- An authenticated caller exceeding its authorization
- A compromised consumer or workload
- A malicious or compromised policy publisher or distribution path
- A malicious, compromised, or incorrectly configured provider
- A cross-tenant attacker
- An operator making an unsafe policy or lifecycle change
- A supply-chain attacker modifying code, schemas, dependencies, or site content
- A website pipeline copying unreviewed research material

## Trust-boundary threats and candidate controls

| Threat | Boundary | Candidate controls to evaluate |
| --- | --- | --- |
| Algorithm downgrade | Policy and broker | Authenticated profiles, minimum constraints, lifecycle enforcement, rollback detection, explicit rejection |
| Policy substitution | Policy distribution | Provenance verification, version pinning, allowlisted authority, expiry, tamper-evident audit |
| Confused deputy | Consumer and broker | Strong caller identity, intent authorization, tenant-bound key references, purpose restriction |
| Capability spoofing | Broker and provider | Authenticated channel, signed or channel-bound descriptor, freshness, execution-time validation |
| Provider substitution | Broker and provider | Policy allowlist, provider identity, key-protection constraints, audit, explicit migration procedure |
| Cross-tenant key use | All runtime boundaries | Tenant-scoped authorization, opaque random references, backend isolation, negative tests |
| Key-reference enumeration | Consumer and broker | High-entropy references, access checks independent of possession, rate limits, non-distinguishing errors where appropriate |
| Replay or duplicate operation | Consumer and broker | Freshness, unique request IDs, bounded idempotency records, operation-specific retry rules |
| Double hashing or encoding confusion | Consumer and provider | Typed inputs, explicit prehash semantics, canonical encodings, test vectors |
| Secret leakage | Runtime and observability | No secrets in logs, protected secret delivery, memory handling, least privilege, redaction tests |
| Denial of service | Network, broker, provider | Admission control, quotas, bounded work, timeouts, circuit breakers, capacity isolation |
| Audit deletion or forgery | Broker and audit sink | Restricted write path, integrity protection, secure time, retention, independent monitoring |
| Unreviewed website publication | Repository and website | `site/` allowlist, protected branch, manual Pages workflow, explicit approval, no runtime fetch |

## Important abuse cases

### Ambiguous policy

An attacker or configuration error creates overlapping rules. The broker chooses
one based on ordering that the consumer cannot see. CAAP must reject unresolved
ambiguity rather than treating rule order as an undocumented security control.

### Weaker but available provider

The intended provider is unavailable while a weaker or differently protected
provider remains online. Availability pressure causes automatic fallback. CAAP
must reject the operation unless an explicit active policy authorizes the exact
alternative while still meeting minimum constraints.

### Stale capability cache

The broker routes an operation based on a descriptor that no longer represents
provider state. Descriptors need scope and freshness semantics, and the provider
must still enforce operation authorization at execution.

### Rebound key reference

A reference is deleted and later resolves to different key material or another
tenant. References need stable identity, lifecycle state, non-reuse rules, and
tenant authorization independent of identifier possession.

### Draft publication

A website job publishes research text from an unreviewed branch or working tree.
The public boundary needs a protected source branch, allowlisted `site/` path,
manual deployment, recorded source commit, and explicit approval.

## Out of scope for this version

- Cryptanalysis of selected algorithms
- Physical security evaluation of HSMs or other devices
- Formal verification of protocol or implementation
- Side-channel resistance claims
- Security of certificate issuance protocols themselves
- Product-specific threat and capability assessments

## Validation work required

This threat model should drive negative protocol tests, policy-conflict tests,
tenant-isolation tests, replay tests, publication-gate tests, and deployment-specific
reviews. None are claimed complete merely because they are listed here.
