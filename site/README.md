# Repository-hosted research site

`site/` is a dependency-free static site designed for GitHub Pages. It links to
the authoritative specification and implementation in this repository, so the
personal site does not carry a second copy. Its canonical public URL is
<https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/>; the
GitHub Pages address is only the content origin used by the personal-site
rewrite.

The optional client-side content deterrent is retained in `app.js` and disabled
in `config.js`. It is not security or access control. Leave it disabled for the
public research site unless there is a presentation-only reason to enable it.

## Preview

```sh
python3 -m http.server 8000 --directory site
```

## Publish only after approval

1. Commit and push reviewed changes to `main`.
2. In GitHub repository settings, select **GitHub Actions** as the Pages source.
3. Manually run the `Deploy research site to Pages` workflow.
4. Verify `https://ganeshmallaya.github.io/common-crypto-api-caap/`.
5. Apply the external-origin rewrite and Research navigation change in
   [`../docs/personal-site-integration.md`](../docs/personal-site-integration.md).

The workflow is manual by design; pushing does not automatically publish.
