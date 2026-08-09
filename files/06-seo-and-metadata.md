# SEO and Metadata

**Publication package for ganeshmallaya.com/research/common-crypto-api**

---

## 1. Keyword targeting

**Primary keyword:** cryptographic agility architecture

**Secondary keywords:**

| Keyword | Intent | Placement |
|---|---|---|
| common crypto API | branded, low competition | H1, URL, title |
| algorithm-agnostic cryptographic API | informational | H2 in architecture page |
| post-quantum migration without code changes | commercial investigation | before-and-after page H1 |
| crypto agility standard | informational | framework page |
| PQC migration call sites | long tail | use-cases page |
| composite hybrid signature API | long tail, technical | orchestrator section |
| PKCS#11 crypto agility | long tail, high qualification | framework page section 7.3 |

The primary keyword appears in the first 100 words of the index page. Each secondary keyword owns one page rather than repeating across all of them.

---

## 2. Titles and descriptions per page

### Index page

**SEO title** (52 characters)
`Cryptographic Agility Architecture - Ganesh Mallaya`

**Alternative for A/B testing** (57 characters)
`Common Crypto API: Crypto Agility Design - Ganesh Mallaya`

**Meta description** (154 characters)
`Most PQC migration cost comes from 66 places a developer typed an algorithm name. A vendor-neutral API design that moves that cost to one policy file.`

### Architecture page

**SEO title** (49 characters)
`Crypto Agility Reference Architecture - G. Mallaya`

**Meta description** (151 characters)
`Five planes, two contracts, one broker. A reference architecture for algorithm-agnostic cryptography, including the three cases it refuses to cover.`

### Framework page

**SEO title** (46 characters)
`Common Crypto API Framework Spec - G. Mallaya`

**Meta description** (149 characters)
`Draft framework for a vendor-neutral crypto operation API. Terminology, object model, three conformance levels, bindings, and a governance split.`

### Use cases page

**SEO title** (51 characters)
`8 Crypto Agility Use Cases Compared - G. Mallaya`

**Meta description** (156 characters)
`Eight enterprise workloads scored by call-site pressure and conformance level. Includes the hardest remaining problem each one keeps after migration.`

### Before and after page

**SEO title** (55 characters)
`PQC Migration Without Code Changes - Ganesh Mallaya`

**Meta description** (152 characters)
`One worked migration in Java: JWT signing from ES256 to a hybrid ECDSA plus ML-DSA signature. 66 call sites become one signed policy profile.`

### Prior art page

**SEO title** (53 characters)
`CCP Standard vs IBM Crypto Agility - G. Mallaya`

**Meta description** (155 characters)
`Three independent efforts reached one architecture in 2026. A point-by-point comparison of the CCP Standard, two IBM papers, and where each falls short.`

---

## 3. Complete meta tag block

Use this on the index page. Adjust the title, description, and URL per page.

```html
<!-- Primary -->
<title>Cryptographic Agility Architecture - Ganesh Mallaya</title>
<meta name="description" content="Most PQC migration cost comes from 66 places a developer typed an algorithm name. A vendor-neutral API design that moves that cost to one policy file." />
<meta name="author" content="Ganesh Mallaya" />
<link rel="canonical" href="https://ganeshmallaya.com/research/common-crypto-api" />

<!-- Open Graph -->
<meta property="og:type" content="article" />
<meta property="og:url" content="https://ganeshmallaya.com/research/common-crypto-api" />
<meta property="og:title" content="Common Crypto API: A Cryptographic Agility Architecture" />
<meta property="og:description" content="66 call sites, one algorithm change. A vendor-neutral API design that turns every future crypto migration into a policy edit instead of a code edit." />
<meta property="og:image" content="https://ganeshmallaya.com/images/research/common-crypto-api-og.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Whiteboard diagram of a cryptographic broker between a consumer API and a provider interface" />
<meta property="og:site_name" content="Ganesh Mallaya" />
<meta property="article:published_time" content="2026-08-04" />

<!-- X / Twitter -->
<meta name="twitter:card" content="summary_large_image" />
<meta name="twitter:title" content="Crypto Agility: Two Contracts and One Broker" />
<meta name="twitter:description" content="66 call sites name the algorithm. That is the migration cost, not the algorithm itself. An architecture that fixes it once." />
<meta name="twitter:image" content="https://ganeshmallaya.com/images/research/common-crypto-api-og.png" />
<meta name="twitter:image:alt" content="Whiteboard diagram of a cryptographic broker architecture" />
<meta name="twitter:creator" content="@REPLACE_HANDLE" />
```

---

## 4. Article schema

```json
{
  "@context": "https://schema.org",
  "@type": "ScholarlyArticle",
  "headline": "Common Crypto API: A Cryptographic Agility Architecture",
  "description": "A vendor-neutral, algorithm-agnostic cryptographic operation API for the post-quantum transition, with a reference architecture, framework specification, and worked migration example.",
  "image": "https://ganeshmallaya.com/images/research/common-crypto-api-og.png",
  "author": {
    "@type": "Person",
    "name": "Ganesh Mallaya",
    "url": "https://ganeshmallaya.com/about"
  },
  "publisher": {
    "@type": "Person",
    "name": "Ganesh Mallaya"
  },
  "datePublished": "2026-08-04",
  "dateModified": "2026-08-04",
  "keywords": "cryptographic agility, post-quantum cryptography, PQC migration, cryptographic API, PKCS#11, ML-DSA, hybrid signatures",
  "citation": [
    "NIST CSWP 39",
    "NIST IR 8547",
    "RFC 7696",
    "arXiv:2606.13425",
    "arXiv:2606.13445"
  ]
}
```

---

## 5. FAQ schema

Add a visible FAQ section to the index page before you add this markup. Do not mark up questions that a reader cannot see.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is cryptographic agility?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Cryptographic agility is the ability to change a cryptographic algorithm without changing application code. Most systems lack it because developers name the algorithm at each call site, which turns an algorithm change into a code change across every service."
      }
    },
    {
      "@type": "Question",
      "name": "How is this different from PKCS#11?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "PKCS#11 abstracts which token performs an operation. It does not abstract which algorithm performs it, and it cannot express one signature that spans two algorithms. This design sits one layer above PKCS#11 and can wrap it as a backend provider."
      }
    },
    {
      "@type": "Question",
      "name": "When must organizations complete a post-quantum migration?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "The NIST IR 8547 initial public draft proposes deprecating 112-bit public-key algorithms after 2030 and disallowing them after 2035. NSA CNSA 2.0 sets earlier dates for specific categories, including exclusive post-quantum firmware and software signing by 2030."
      }
    },
    {
      "@type": "Question",
      "name": "Does this architecture work for embedded devices?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "No. A microcontroller with 32 KB of memory cannot host a broker or reach a policy service. Boot-time roots of trust and line-rate network datapaths are also outside scope. This is a datacenter and enterprise-workload architecture."
      }
    }
  ]
}
```

---

## 6. Image briefs

All seven diagrams ship as SVG in `images/`. SVG serves two purposes here. It stays sharp at any width, and it keeps every file under 20 KB, which protects the Largest Contentful Paint target of 2.5 seconds.

| File | Alt text |
|---|---|
| `01-the-problem-whiteboard.svg` | Whiteboard sketch showing six services each naming an algorithm, totaling 66 edits for one algorithm change |
| `02-two-contracts-whiteboard.svg` | Whiteboard sketch of a broker between a north consumer API and a south provider interface |
| `03-reference-architecture-whiteboard.svg` | Whiteboard sketch of the five-plane Common Crypto API reference architecture with a control plane and a stated boundary |
| `04-before-after-whiteboard.svg` | Whiteboard comparison of token signing migration cost with and without a cryptographic broker |
| `05-composite-orchestrator-whiteboard.svg` | Whiteboard sketch of a composite orchestrator dispatching ECDSA to an HSM and ML-DSA to software |
| `06-conformance-and-topologies-whiteboard.svg` | Whiteboard sketch of three conformance levels and four deployment topologies |
| `07-prior-art-positioning-whiteboard.svg` | Whiteboard sketch positioning the CCP Standard, two IBM papers, and this draft by architectural layer |

### Open Graph image brief

The seven SVG files are page diagrams and not social cards. Produce one separate 1200 by 630 PNG.

- Background: the same off-white paper tone, `#fbfbf7`.
- Center 60 percent: the two-contract sketch, simplified to three boxes and two arrows.
- Headline in the hand-drawn face: `66 call sites. One policy file.`
- Bottom left: `ganeshmallaya.com/research` in small type.
- Keep total file size under 100 KB. Text must stay readable at thumbnail size.

### Font note

The SVG files request `Caveat` first and fall back through `Bradley Hand`, `Segoe Print`, and `Comic Sans MS` to a generic cursive. Load Caveat once in the site head so every diagram renders consistently:

```html
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Caveat:wght@400;600&display=swap" rel="stylesheet">
```

An SVG loaded through an `<img>` tag cannot fetch an external font. Inline the SVG in the page, or accept the fallback face.

---

## 7. Tags for the research index

Six tags, no more.

- Cryptographic Agility
- Post-Quantum Cryptography
- PKI Architecture
- Standards and Specifications
- Enterprise Security Architecture
- API Design

---

## 8. Publication checklist

**Copy**

- [ ] Primary keyword appears in the first 100 words of the index page
- [ ] Each page title stays between 30 and 60 characters
- [ ] Each title matches its H1
- [ ] Titles use a dash separator rather than a pipe
- [ ] Every meta description falls between 140 and 160 characters

**Structure**

- [ ] The index page carries a table of contents, because the set exceeds 1,500 words
- [ ] H2 and H3 headings read as a standalone outline
- [ ] Internal links connect all six pages in both directions

**Technical**

- [ ] Canonical tag set on every page
- [ ] Caveat font loaded once in the site head
- [ ] All seven SVG files inlined or served with the font fallback accepted
- [ ] Open Graph PNG produced at 1200 by 630 and compressed under 100 KB
- [ ] Schema validated in the Google Rich Results Test
- [ ] FAQ section visible on the page before the FAQ schema ships

**Performance**

- [ ] Largest Contentful Paint under 2.5 seconds
- [ ] Cumulative Layout Shift under 0.1
- [ ] Every SVG under 20 KB

---

## 9. Distribution note

The prior art page is the strongest entry point for a technical audience, because it names two efforts people are already searching for. The before-and-after page is the strongest entry point for a practitioner audience, because it shows code.

Link both from the research index rather than treating the index as the only door.
