# Native personal-site integration

The canonical public route is:

<https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/>

The personal site renders CALI explanatory pages natively using its shared
Astro header, footer, accessibility behavior, search, responsive layout, and
left-side page navigation. It does not proxy GitHub Pages and does not fetch
repository files at runtime.

## Authority boundary

This repository remains authoritative for the candidate specification, schemas,
OpenAPI document, machine-readable registry and profiles, examples, reference
service, tests, and roadmap. Each native research page ends with a direct link
to the corresponding repository artifact.

The personal-site copy explains those artifacts for engineers. When a protocol
shape changes, update the authoritative artifact first, then update the native
page and both repositories' tests in the same reviewed release.

## Native route map

| Public page | Repository source |
| --- | --- |
| `/research/crypto-agility-algorithm-protocol/` | `README.md` |
| `/specification/` | `spec/cali-v2.md` |
| `/operations/` | `spec/operation-contracts.md` |
| `/operation-catalog/` | `api/operation-registry.json` |
| `/algorithm-profile/` | `api/profiles/pqc-signing-v2.profile.json` |
| `/openapi/` | `api/openapi/cali-v2.openapi.json` |
| `/run-service/` | `reference/README.md` |
| `/implementation/` | `examples/README.md` |
| `/roadmap/` | `ROADMAP.md` |
| `/nist-alignment/` | `docs/nist-cswp-39-alignment.md` |
| `/security/` | `docs/security-considerations.md` |

Every child path above is relative to the canonical research route.

## Publication gate

Keep changes local until the maintainer approves commit and deployment. Validate
this repository with `python3 -m unittest discover -s tests -v` and validate the
personal site with its formatting, lint, build, link, and Playwright gates.
