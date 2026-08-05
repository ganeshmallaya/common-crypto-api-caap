# Public export boundary

This directory is the only CAAP content boundary intended for a public website.
The source repository remains authoritative.

Current status: **reviewed; eligible for commit-pinned synchronization after
explicit approval of the website-repository change**.

The Framework v1 candidate export consists of:

- `caap-framework-v1.md`, the website research article; and
- `images/`, the original explanatory diagrams used by that article; and
- `website-metadata.json`, portable title, description, route, status, and
  social-image metadata for the website integration.

The manifest allowlists the exact paths and hashes at the reviewed source
commit. A website repository must copy only those files and record that source.

Publication requirements are defined in
[`../docs/publication-workflow.md`](../docs/publication-workflow.md) and enforced
by `site-manifest.json` plus repository tests. A website integration must copy
allowlisted files at a pinned commit. It must not fetch this repository at
runtime or use a Git submodule.
