# Public website synchronization

Status: repository contract

## Objective

Keep the CAAP research repository authoritative while allowing reviewed,
publication-ready content to be copied into a separate personal website. The
website remains independently buildable and does not depend on this private
repository at runtime.

## Intended website sections

- Main navigation label: `Research`
- Research index route: `/research/`
- CAAP route: `/research/crypto-agility-algorithm-protocol/`
- Initial visible copy: `Content coming soon.`

These are target integration details, not evidence that the personal website
has already been changed or deployed.

## Export contract

`public-export/site-manifest.json` identifies:

- manifest schema version
- canonical project name and repository name
- publication status
- source commit
- target routes
- exact export files
- review metadata

Only paths explicitly listed in the manifest can be copied. Source Markdown,
HTML architecture drafts, examples, and schemas outside `public-export/` are
not website inputs.

## Status gate

| Status | Website action |
| --- | --- |
| `draft` | Do not copy or publish. |
| `reviewed` | Eligible for a versioned copy after explicit approval. |
| `published` | Records that the reviewed export was published separately. |
| `withdrawn` | Do not copy; remove or replace only through the website's own reviewed change. |

A `reviewed` or `published` manifest requires a full Git source commit. The
current initial manifest remains `draft` with `sourceCommit: null` until the
placeholder and contract are reviewed in a real Git commit.

## Proposed synchronization procedure

1. Review the exact files listed by the manifest.
2. Commit the reviewed research state locally.
3. Update the manifest to `reviewed`, set the full source commit, reviewer, and
   review time in UTC; commit that manifest update.
4. In an integration project, attach the personal-site repository as primary
   and this CAAP repository as secondary.
5. Copy only allowlisted export files into the website's content model.
6. Record the CAAP source commit in the website repository next to the copied
   content or in a synchronization ledger.
7. Run the website's local build, link, accessibility, and browser checks.
8. Review the rendered `/research/` and CAAP routes.
9. Push or deploy only after explicit approval.

The source commit normally identifies the commit containing the reviewed export
content. A later manifest-only commit can point back to that immutable content
commit without creating a circular self-reference.

## Prohibited integration patterns

- Live fetching from a private GitHub repository during a Vercel build or at
  request time
- Git submodules between the repositories
- Copying unreviewed files from `docs/` or the repository root
- Treating branch names, tags, or `HEAD` as a reproducible source version
- Automatic push, publication, or deployment from this research repository
