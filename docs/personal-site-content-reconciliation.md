# Personal-site content reconciliation

Audited against the `personal-site` development branch at commit `8f91e02`.
This document records how the earlier CAAP pages map into the repository-owned
research source. It prevents substantive ideas from being lost when the
personal-site copies are removed.

## Authority rule

The current sources are:

1. [`spec/caap-v1.md`](../spec/caap-v1.md) for candidate protocol semantics;
2. [`api/openapi/caap-v1.openapi.json`](../api/openapi/caap-v1.openapi.json) for
   the executable HTTP binding;
3. [`ROADMAP.md`](../ROADMAP.md) for implemented/specified/planned status;
4. [`docs/`](./) for architecture, threats, security, and NIST alignment; and
5. [`site/`](../site/) for the public research presentation.

The earlier personal-site framework and protocol pages become historical after
redirects are active. They must not be maintained as a second specification.

## Content map

| Earlier personal-site content | Repository-owned destination | Reconciliation |
| --- | --- | --- |
| Two-contract thesis | Specification sections 1–4; site `#definition` | Preserved and tightened around pinned policy and fail-closed processing. |
| Five-plane architecture | `docs/architecture.md`; site `#architecture` | Preserved: consumer, interface, broker, provider, and policy authority. |
| Six-step request flow | Specification section 4; site `#how-it-works` | Preserved and aligned with the candidate processing sequence. |
| Framework v1 operation list | Specification section 7; internal roadmap milestones 1–3 | Corrected: `CreateKey`, `Sign`, `Verify`, discovery, and resolution are the implemented slice; KEM and other primitives remain internal planned work. |
| Portable failures | Specification section 6 | Canonicalized to stable categories including policy inactivity and capability mismatch. |
| IAM signing map | Architecture and specification consumer boundary | Preserved with the identity service remaining transaction owner. |
| Certificate issuance map | `docs/architecture.md` | Preserved with CA/CLM validation, issuance, revocation, and lifecycle outside CAAP. |
| PKCS#11/KMIP and opaque-reference caveats | Site `#precedent` and `#limits`; security considerations | Preserved and expanded with custody, migration, and provider-substitution limits. |
| Artifact-signing interoperability proposal | Specification section 8; internal roadmap milestone 1 | Advanced into a tested software-provider research slice; no interoperability claim is made. |
| Client-side copy/print deterrent | `site/app.js` and `site/config.js` | Retained but disabled; explicitly not described as security. |
| Copied provenance manifest | Superseded | Removed because the public site now deploys from this authoritative repository. |
| External implementation lineage section | Superseded | Removed. CAAP states independent development and cites primary standards and government guidance only. |

## Synchronized visual model

The earlier architecture and request-flow drawings were translated into
semantic HTML and responsive CSS in `site/index.html`. No handwritten diagram
or content image is required. The underlying five-plane architecture,
two-contract boundary, processing sequence, and implementation status remain
machine-readable and accessible in the page structure.

The earlier “open vendor boundary” framing was not migrated because it conflicts
with the current all-rights-reserved ownership decision. Its underlying
separation between portable semantics and implementation choice is preserved in
the internal roadmap and specification.

## Release check

The personal-site copies are removed in the prepared local integration. Before
publishing either repository, verify that the repository site contains
`problem`, `precedent`, `definition`, `architecture`,
`how-it-works`, `pillars`, `maturity`, `why-now`, `limits`, and
`implementation`; verify the specification and repository links; then test all
legacy redirects.
