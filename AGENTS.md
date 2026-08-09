# AGENTS.md

These instructions apply to the entire repository.

## Purpose and naming

- This is independently owned, vendor-neutral research by Ganesh Mallaya. It may
  be publicly viewable while remaining all-rights-reserved unless a license is
  deliberately added.
- **Cryptographic Abstraction Layer Interface (CALI)** is the canonical name of
  the research specification and interface moving forward.
- **Common Crypto API** may describe the interface category, but CALI is the
  project name.
- `cali-crypto-interface` is the repository name; do not infer a different
  expansion of CALI from it.

## Authority and status

- Treat `docs/`, `schemas/` and `examples/` as working research material.
- Treat `spec/cali-v2.md` as the current research specification and the OpenAPI
  document as its experimental HTTP binding.
- Do not invent standards status, affiliations, adoption, interoperability,
  conformance, product capabilities, implementation results, benchmarks or
  security assurances.
- Do not name or imply affiliation, sponsorship, compatibility or endorsement
  with an existing implementation. Public alignment references should point to
  primary standards and government guidance.
- Mark proposals, unresolved decisions and examples explicitly.
- Keep vendor names out of normative requirements. A named product may appear
  only in sourced research notes or clearly non-normative examples.

## Security and protocol writing

- Separate consumer, broker, policy, provider and certificate-authority trust
  boundaries.
- Do not imply that CALI replaces PKCS#11, KMS APIs, CA protocols or existing
  cryptographic standards.
- Require explicit failure for ambiguity, downgrade, policy expiry and
  capability mismatch. Never specify silent algorithm fallback.
- Use opaque key references by default. Do not place secret key material in
  examples, logs or research-site content.
- Treat schemas in `schemas/` as experimental until a later document explicitly
  designates a normative binding.

## Research-site publication gate

- The research repository is authoritative for specification and implementation
  artifacts. The personal site renders reviewed explanatory copies natively and
  links each page to its repository source.
- Do not restore the GitHub Pages proxy or Vercel rewrite. The canonical route is
  rendered by `personal-site` so its header, navigation, accessibility and
  deployment behavior match the rest of ganeshmallaya.com.
- Publication still requires explicit user approval. Do not enable GitHub Pages,
  configure a custom domain, alter DNS or update the personal-site repository
  without that approval.

## Changes and validation

- Keep changes local unless the user explicitly approves a push or publication.
- Preserve existing files unless a requested change requires migration or
  deletion.
- Run `python3 -m unittest discover -s tests -v` after changing schemas,
  examples, internal Markdown links, the reference service or the site contract.
- Update the documentation, examples, schemas and tests together when a
  protocol shape changes.
