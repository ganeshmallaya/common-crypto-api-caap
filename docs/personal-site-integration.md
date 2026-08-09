# Serve the repository site at the canonical personal-site URL

The canonical public URL is fixed:

<https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/>

The content source is `site/` in this repository. GitHub Pages is the origin;
Vercel preserves the canonical `ganeshmallaya.com` address by rewriting that
path to the Pages origin. A rewrite keeps the browser URL unchanged. This avoids
copying CAAP articles, data, or components into `personal-site`.

```text
common-crypto-api-caap/main/site/
                | manual GitHub Pages deployment
                v
ganeshmallaya.github.io/common-crypto-api-caap/
                | Vercel external-origin rewrite
                v
ganeshmallaya.com/research/crypto-agility-algorithm-protocol/
```

The static page declares the `ganeshmallaya.com` URL as its canonical URL. The
GitHub Pages URL is an implementation origin, not the public identity.

## Personal-site changes

In `personal-site/vercel.json`, merge the two legacy-route redirects into the
existing `redirects` array and add the rewrite array. Keep the exact rewrite
first and the wildcard second:

```json
{
  "redirects": [
    {
      "source": "/research",
      "destination": "/research/crypto-agility-algorithm-protocol/",
      "permanent": true
    },
    {
      "source": "/research/crypto-agility-algorithm-protocol/protocol",
      "destination": "/research/crypto-agility-algorithm-protocol/",
      "permanent": true
    }
  ],
  "rewrites": [
    {
      "source": "/research/crypto-agility-algorithm-protocol",
      "destination": "https://ganeshmallaya.github.io/common-crypto-api-caap/"
    },
    {
      "source": "/research/crypto-agility-algorithm-protocol/:path*",
      "destination": "https://ganeshmallaya.github.io/common-crypto-api-caap/:path*"
    }
  ]
}
```

The wildcard rewrite is essential: relative requests for `styles.css`, scripts, and
SVGs arrive below the canonical path and must be forwarded to the matching Pages
asset. Vercel documents this as an external-origin rewrite, which serves external
content while retaining the requested URL.

Set the Research navigation target in `src/components/Header.astro` to:

```ts
[
  'https://ganeshmallaya.com/research/crypto-agility-algorithm-protocol/',
  'Research',
],
```

Remove the duplicated CAAP route implementation, research index, copied data,
sync tooling, and presentation-only protection component after confirming no
other code imports them. The audit of personal-site commit `8f91e02` identified
these migration candidates:

```text
src/pages/research/crypto-agility-algorithm-protocol/index.astro
src/pages/research/crypto-agility-algorithm-protocol/protocol/index.astro
src/pages/research/index.astro
src/data/research/caap/
src/components/research/CaapTabs.astro
src/components/research/ResearchProtection.astro
scripts/sync-caap-export.mjs
scripts/sync-caap-export.test.mjs
```

CAAP is currently the sole Research destination, so `/research` redirects to
the canonical CAAP route. The lightweight record in
`src/pages/search-index.json.ts` points to that canonical URL and contains no
copied specification body. The content-deterrent code is retained, disabled,
in the authoritative repository site rather than duplicated here.

The prior personal-site content used operation names and scope that differ from
the current candidate contract. The repository specification, OpenAPI document,
schemas, examples, and `site/` are now the authoritative working set. See
[`personal-site-content-reconciliation.md`](personal-site-content-reconciliation.md).

## Controlled release order

1. Review, commit, and push this repository.
2. Select **GitHub Actions** as the repository's Pages source.
3. Manually run `Deploy research site to Pages` and verify the Pages origin.
4. In the personal-site checkout, merge the two redirects and two rewrite
   rules, then change the Research navigation target.
5. Remove the duplicated CAAP files and sync tooling after checking their
   callers, then replace copied-route assertions with rewrite/link assertions.
6. Run `npm run format:check && npm run lint && npm test` in personal-site.
7. Preview the exact canonical route and verify desktop, mobile, styles,
   scripts, repository links, and the permanent nested `/protocol/` redirect.
8. Commit, push, and deploy the personal-site change only after review.

Vercel's current rewrite documentation is the configuration authority:
<https://vercel.com/docs/routing/rewrites#rewrites-to-external-origins>.

## Rollback

Remove the two redirects and two rewrites, then restore the Research navigation
to `/research/` and restore the old pages from Git history.
