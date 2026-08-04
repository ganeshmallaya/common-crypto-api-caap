# AGENTS.md

These instructions apply to the entire repository.

## Purpose and naming

- This is a private, vendor-neutral research repository.
- **Crypto Agility Algorithm Protocol (CAAP)** is the canonical name of the
  research specification.
- **Common Crypto API** is the implementation/interface defined by CAAP.
- `common-crypto-api-caap` is the repository name; do not infer a different
  expansion of CAAP from it.

## Authority and status

- Treat `docs/`, `schemas/`, and `examples/` as working research material.
- Treat the pre-existing root-level specification and HTML architecture files
  as historical inputs, not as authoritative or standards-track artifacts.
- Do not invent standards status, affiliations, adoption, interoperability,
  conformance, product capabilities, implementation results, benchmarks, or
  security assurances.
- Mark proposals, unresolved decisions, and examples explicitly.
- Keep vendor names out of normative requirements. A named product may appear
  only in sourced research notes or clearly non-normative examples.

## Security and protocol writing

- Separate consumer, broker, policy, provider, and certificate-authority trust
  boundaries.
- Do not imply that CAAP replaces PKCS#11, KMS APIs, CA protocols, or existing
  cryptographic standards.
- Require explicit failure for ambiguity, downgrade, policy expiry, and
  capability mismatch. Never specify silent algorithm fallback.
- Use opaque key references by default. Do not place secret key material in
  examples, logs, or public exports.
- Treat schemas in `schemas/` as experimental until a later document explicitly
  designates a normative binding.

## Public export gate

- The research repository is authoritative.
- `public-export/` is the only content eligible for copying to a public site.
- Publication requires `site-manifest.json` status `reviewed`, a full source
  commit hash, matching reviewed files, and explicit user approval.
- `draft`, `withdrawn`, or missing-source-commit exports must not be synced.
- Do not add runtime fetching, Git submodules, or automatic cross-repository
  publication.

## Changes and validation

- Keep changes local unless the user explicitly approves a push or publication.
- Preserve existing files unless a requested change requires migration or
  deletion.
- Run `python3 -m unittest discover -s tests -v` after changing schemas,
  examples, internal Markdown links, or the public-export contract.
- Update the documentation, examples, schemas, and tests together when a
  protocol shape changes.
