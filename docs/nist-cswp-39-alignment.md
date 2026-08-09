# Alignment with NIST CSWP 39upd1

CALI is proprietary Ganesh Mallaya research informed by
[NIST CSWP 39upd1, *Considerations for Achieving Crypto Agility: Strategies and Practices*](https://doi.org/10.6028/NIST.CSWP.39-upd1),
finalized with updates on 2026-06-29. NIST defines crypto agility broadly as the
capabilities needed to replace and adapt algorithms across protocols,
applications, software, hardware, firmware, and infrastructure while preserving
security and ongoing operations.

This document records design alignment only. CALI is not a NIST publication,
standard, profile, endorsement, or conformance claim.

## How CALI turns the guidance into a research contract

| NIST CSWP 39upd1 theme | CALI response |
| --- | --- |
| Transitions must preserve security and operations. | The broker fails closed on ambiguity, downgrade, expired policy, incompatible capability, and invalid key state. |
| Agility spans applications and infrastructure. | The Common Crypto API separates consumer intent from provider adapters while retaining explicit trust boundaries. |
| Operational mechanisms need trade-off analysis. | Every deployment mode documents identity, custody, availability, latency, policy-cache, and evidence assumptions. |
| Protocol and application constraints matter. | Algorithms are substitutable only inside profiles with compatible operation shapes, inputs, outputs, and encodings. |
| Governance and risk management are part of agility. | Policy authority is separate from broker enforcement; decisions are versioned, pinned, attributable, and auditable. |
| Inventory, testing, and metrics support transition. | The roadmap includes scoped discovery, capability evidence, negative vectors, black-box conformance tests, and independent implementations. |

## Boundaries

NIST CSWP 39upd1 is guidance, not an API specification. CALI supplies one
candidate technical model and reference slice. It does not imply that a policy
change alone can update protocols, peer systems, certificate chains, stored
data, fixed-function devices, or every application without coordinated change.

## Review rule

Future CALI claims should cite the current NIST revision, distinguish guidance
from CALI-specific design choices, and label unimplemented work clearly.
