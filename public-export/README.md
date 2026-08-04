# Public export boundary

This directory is the only CAAP content boundary intended for a public website.
The source repository remains authoritative.

Current status: **draft; not eligible for synchronization**.

Publication requirements are defined in
[`../docs/publication-workflow.md`](../docs/publication-workflow.md) and enforced
by `site-manifest.json` plus repository tests. A website integration must copy
allowlisted files at a pinned commit. It must not fetch this repository at
runtime or use a Git submodule.
