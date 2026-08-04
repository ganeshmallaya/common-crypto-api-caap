# Security considerations

Status: working research draft

CAAP centralizes a high-impact decision: which cryptographic mechanism and
provider will act for a caller. Centralization can improve visibility and
control, but it also concentrates policy, identity, routing, and availability
risk. A stable API is not itself a security boundary.

## Policy integrity and lifecycle

A deployment needs authenticated policy provenance, explicit effective and
expiry times, rollback resistance, and an emergency withdrawal process. The
broker must identify the exact profile and version used. Cached policy requires
bounded lifetime and defined disconnected behavior.

Policy ambiguity, absence, inactivity, and constraint conflict are failures.
They are not reasons to select a default.

## Authorization before capability

Capability discovery answers what a provider can do, not what a caller may do.
The broker and provider need scoped authorization. A caller must not gain use of
a key merely by learning or presenting its reference.

## Key custody and references

Private keys should remain behind opaque references by default. References must
be unpredictable, tenant-bound, non-reusable, and checked against current key
state. Import, export, wrap, unwrap, backup, restore, and destruction require
separate semantics and authorization; they are not implied by a generic key
operation.

“Hardware-backed” and “non-extractable” are assurance claims requiring defined
evidence and verification. A provider label or key-reference format does not
establish either claim.

## Downgrade resistance

The caller and policy may express minimum constraints. Resolution must preserve
them through dispatch. Automatic fallback to a weaker algorithm, different key
protection, an unapproved provider, or an expired profile is unsafe even during
an outage.

Comparison of algorithm strength is not reduced to one universal number. The
policy model needs operation- and context-specific rules backed by reviewed
sources.

## Input and encoding safety

Sign and verify operations need an explicit distinction between messages,
digests, and structured protocol objects. Algorithm identifiers alone do not
define all parameter, context-string, signature, public-key, ciphertext, or
combined-output encodings. Normative bindings need canonical encodings and test
vectors.

## Combined constructions

CAAP must not create a combined construction by merely running two algorithms
and concatenating outputs. Composition, combiner behavior, validation,
encoding, failure handling, and security properties require an external or
separately reviewed definition. Until then, combined-operation examples are
illustrative only.

## Authentication, replay, and retries

Remote deployments need authenticated and integrity-protected channels plus
caller identity suitable for workload authorization. Request IDs support
correlation but do not provide freshness on their own. Retry and idempotency
rules must be operation-specific; repeating key generation or signing can have
security and audit consequences.

## Audit and privacy

Audit events should capture caller identity, tenant, operation, intent, policy
version, selected identifiers, provider reference, result category, and timing.
They must not capture private keys, shared secrets, credentials, or unintended
sensitive payloads. Provider details may also reveal infrastructure and require
access controls.

Audit integrity, retention, secure time, and failure behavior are deployment
requirements. Logging failure must not silently erase accountability.

## Availability

The broker, policy service, and providers may become shared dependencies.
Deployments need capacity isolation, bounded queues, timeouts, rate limits, and
a consciously selected fail-closed behavior. An emergency policy is still a
policy; it must be authenticated, time-bounded, auditable, and constrained.

## Implementation and supply chain

Future implementations need dependency review, secure update mechanisms,
secret scanning, reproducible interface artifacts where practical, and tests
that compare prose, schemas, and code. A reference implementation demonstrates
one interpretation; it does not prove that the design or cryptography is safe.

## Public export

Research drafts may discuss unresolved weaknesses and must not become public by
accident. Only allowlisted files under `public-export/`, at a pinned commit with
status `reviewed`, are eligible for copying. Publication still requires explicit
approval. The public website must not fetch repository content at runtime.

## Unresolved security decisions

- Policy signing and trust-anchor model
- Rollback detection and emergency withdrawal
- Workload identity and channel binding
- Provider capability authenticity and freshness
- Key-reference format and lifecycle
- Secret-delivery model
- Combined-construction identifiers and encodings
- Audit event schema and integrity mechanism
- Provider evidence and assurance vocabulary
