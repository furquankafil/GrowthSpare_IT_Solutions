# SEO Forensic Verification Report — GrowthSpare IT Solutions

**Date:** 2026-09-09 · **Method:** source-code inspection + live Django crawl (116 URLs) + header checks. Did not trust the prior report; every claim re-tested. Fixes applied where automatic and safe; retested with `manage.py check`, 5 tests, and re-crawl.

## A. Previous claims — verified (with evidence)

| # | Claim | Status | Evidence (file / URL) |
|---|-------|--------|-----------------------|
| 1 | robots.txt | **CONFIRMED** | `templates/core/robots.txt` allows `/`, disallows `/admin/ /accounts/ /dashboard/ ?q/?category/?page=`; live `/robots.txt` 200 shows canonical `Sitemap: https://growthspareitsolutions.com/sitemap.xml`; `/consultation/book/` is allowed (contradiction fixed) |
| 2 | sitemap.xml | **CONFIRMED** | `apps/core/sitemaps.py` includes home/about/legal/contact/consultation/services/portfolio/blog/faq/testimonials + NEW `locations-index`/`industries-index` + locations/industries; live `/sitemap.xml` 200 (host=request; submit apex URL) |
| 3 | Canonical URLs | **CONFIRMED** | `seo_tags.get_canonical_url` = `SITE_URL + request.path`; crawl: 100% absolute apex canonicals (e.g. `/` → `https://growthspareitsolutions.com/`), never test host |
| 4 | 301 redirects | **CONFIRMED** | 17 aliases all single-hop 301: services ×4, locations ×4, industries ×9; plus `?category=`→category, no-slash→slash, www→apex (middleware, live 301 verified) |
| 5 | Metadata (unique) | **CONFIRMED with fixes** | 0 duplicate titles/descs across 99 pages; OG + Twitter on every page; brand dedup logic works (`Get a Free Website Audit - GrowthSpare…` not doubled). Length trims applied (see D) |
| 6 | H1 structure | **CONFIRMED** | H1 count = 1 on every crawled HTML page; texts sane (home brand H1, services intent H1, locations/industries headings) |
| 7 | JSON-LD | **CONFIRMED** | Parses on all schema pages; types: home Org/WebSite/LocalBiz/FAQ, about Org/Breadcrumb, contact LocalBiz/Breadcrumb, locations LocalBiz/FAQ, industries Service/Breadcrumb/FAQ, services Service/…/FAQ, blog Article, FAQ page FAQPage |
| 8 | Internal links | **CONFIRMED with fix** | Homepage hub + footer (now specific) + service contextual links + location/industry CTAs verified; `/testimonials/` orphan FIXED via footer links |
| 9 | LocalBusiness schema | **CONFIRMED appropriate** | Home/contact/3 locations share one NAP/hours helper; real address/phone/hours; `areaServed` Delhi/Noida/Gurugram (service-area, not fake branches) |
| 10 | Organization schema | **CONFIRMED** | Home + about carry Org with `@id …/#organization`, logo, sameAs (footer profiles only) |
| 11 | WebSite schema | **CONFIRMED ( + note)** | Home has WebSite + SearchAction → `/blog/?q={…}` (blog search exists, so valid). Service pages also append WebSite — redundant but valid; leave |
| 12 | Breadcrumb schema | **CONFIRMED (+1 added)** | About/contact/locations/industries/services-detail have it + visible nav; ADDED to `/services/` list (was missing) |
| 13 | noindex rules | **CONFIRMED** | `robots=` param emits `<meta robots>`; live: `/blog/?q=` and `/portfolio/?category=` → `noindex,follow`; 404 template `noindex,follow`; `/services/?category=` 301s (no render) |
| 14 | Image alt | **CONFIRMED** | Homepage 9 imgs / 0 missing; all crawled pages 0 missing; lazy on below-fold; logos now have dimensions + decoding |
| 15 | Accessibility | **CONFIRMED** | Skip-link + `#main-content`, `:focus-visible`, FAQ `aria-expanded` sync, labelled theme/hamburger/WhatsApp/back-to-top buttons, form labels — all in source + live HTML |
| 16 | Conversion tracking | **CONFIRMED** | `static/js/conversion_tracking.js` served 200, in base (`defer`); `dataset` guards prevent double-fire; `typeof gtag` guard + try/catch prevents breakage; params are label/path only (no PII) |
| 17 | CSP | **CONFIRMED (was broken, now fixed)** | Live `Content-Security-Policy` header includes `googletagmanager.com`, `google-analytics.com` (script+connect). Prior code blocked GA4; fixed in `base.py` |
| 18 | GA4 compatibility | **CONFIRMED** | `G-P68BKJ57R4` script in `<head>` + CSP allows it + event layer calls `gtag('event',…)` (no-op without GA4) |
| 19 | Performance changes | **CONFIRMED (partial)** | theme-color, preconnects (cdnjs/jsdelivr/unpkg/gtag), `defer` on main/animations/conversion, logo fetchpriority/dimensions — all live. Tailwind Play CDN + 6 vendor libs intentionally kept (design) |

## B. Claims that were incorrect or incomplete

1. **"Titles/metas all good" — MISSED portfolio placeholder descriptions.** 17 portfolio pages emitted `for {industry} for {client}` (33–51 chars) from `seed_database.py` stubs. Previous report claimed uniqueness but not quality. **Fixed** (view ignores `<70-char`/`for `-prefixed stubs → real fallback; re-crawl shows ~150–189 chars).
2. **"Performance PASS" — MISSED 1 MB+ images.** `logo.png` 1.07 MB, `founder.png` 1.9 MB, `favicon.ico` 938 KB on disk. Previous work added lazy/decoding but not weight. **Flagged, not auto-recompressed** (brand assets; owner/designer must export compressed PNG/WebP <150 KB + <50 KB favicon). See H.
3. **"No thin content" — MISSED 20 thin blog posts (~350 words).** Seeded filler (`keyword-intent-mapping…`, `meta-conversions-api…`, etc.) with 1–2 paragraph bodies, all published + in sitemap. **Flagged as content debt** (expand/consolidate; owner decision — not auto-unpublished). See §12/13.
4. **Title/desc lengths overstated as fine.** Home was 90 chars, `/services/` desc 187, `/portfolio/` 214, `/faq/` 227. **Trimmed** to 51–73 / ≤160 (brand suffix +27 noted as accepted truncation risk).
5. **Orphan check missing.** `/testimonials/` had 0 inbound (not in nav). **Fixed** via footer links. Pagination "orphans" in single-page crawl are false positives (resolve on list pages 2+).
6. **`/services/` had no JSON-LD.** Claimed schema coverage implied completeness. **Added** BreadcrumbList.

## C. Issues discovered (all)

- CRITICAL: portfolio placeholder metas (fixed). Thin blog cluster (flagged). 1 MB images (flagged).
- HIGH: long titles/descs (fixed). Testimonials orphan (fixed).
- MEDIUM: service-category pages thin (244–306w, no schema) — acceptable indexes, monitor. Consultation/testimonials/portfolio-index/blog-index/legal carry no JSON-LD — correct (no visible content justifying it) except services breadcrumb (added).
- LOW: portfolio `CreativeWork` minimal + concept fallback descs ~189 chars (valid, slightly long). Title 70–80 char brand-suffix truncation risk (accepted). Sitemap host=request (submit apex URL manually).

## D. Fixes implemented (forensic pass)

1. `apps/portfolio/views.py` — ignore placeholder `meta_description` (`<70` chars or `for …` prefix) → concept/real-case fallback. Fixes 17 broken SERP snippets without DB migration (respects admin-fixed values).
2. Titles/descs trimmed: home 90→67; `/services/` title 81→66 + desc 187→122; `/portfolio/` desc 214→132; `/faq/` title→65/desc→118; `/locations/` 85→73; `/industries/` 101→80 + desc 173→136.
3. `templates/components/footer.html` — added Portfolio/Insights/Client Reviews to legal row (de-orphans `/testimonials/`; also surfaces blog/portfolio).
4. `apps/services/views.py` — added BreadcrumbList JSON-LD to `/services/`.
5. No doorway pages created: all short URLs remain 301s (verified single-hop, no chains/loops).

## E. Files changed (forensic pass)

- `apps/portfolio/views.py`, `apps/services/views.py`, `apps/faq/views.py`, `apps/core/views.py` (titles/descs), `templates/components/footer.html`
- Created: `SEO_CRAWL_REPORT.md`, `LOCAL_SEO_AUDIT.md`, `OFFSITE_SEO_PLAN.md`, `SEO_FORENSIC_VERIFICATION_REPORT.md` (this file), `SEO_CRAWL_RAW.json` (machine data)

## F. URLs tested

116 crawled (F §2 list): 30 static/hub/landing/legal/robots/sitemap + 7 services + 5 categories + 17 portfolio + 40 blog + 17 aliases. Plus header checks (CSP, www, trailing slash, static). Full table in `SEO_CRAWL_REPORT.md`.

## G. Before/after (measurable)

| Metric | Before forensic | After |
|--------|----------------|-------|
| Portfolio descs | 17 × 33–51-char stubs (`for X for Y`) | 17 × 150–189-char real summaries |
| Home title | 90 chars | 67 |
| `/services/` title/desc | 81 / 187 | 66 / 122 |
| `/portfolio/` desc | 214 | 132 |
| `/faq/` title/desc | 74-ish generic / 227 | 65 / 118 |
| `/locations/` title | 85 | 73 |
| `/industries/` title/desc | 101 / 173 | 80 / 136 |
| Testimonials inbound | 0 (orphan) | footer-linked |
| `/services/` JSON-LD | none | BreadcrumbList |
| Duplicates / H1≠1 / missing alt / broken / chains | 0 / 0 / 0 / 0 / 0 | same (held) |
| Tests / check | 5 OK / clean | 5 OK / clean |

## H. Remaining technical issues (owner-ordered)

1. **Compress images (real LCP/weight win):** `logo.png` 1.07 MB → <150 KB; `founder.png` 1.9 MB → <200 KB; `favicon.ico` 938 KB → <50 KB (or `.png` + `.ico` fallback). Export at display size, keep PNG alpha, add WebP with PNG fallback if easy. Do NOT hotlink-compress without keeping backups.
2. **Thin blog cluster (20 × ~350w):** expand the 10 roadmap topics first (genuine expertise, 800+ words, examples, internal links, CTA); then either expand, merge, or `noindex`/unpublish the weakest (owner call). Don't mass-generate filler.
3. **Service-category pages (244–306w, no schema):** optionally add 1-paragraph unique intro per category + BreadcrumbList. Low priority.
4. **Optional:** self-hosted Tailwind build (remove Play CDN runtime), 1200×630 OG image, `rel=prev/next` unnecessary (skip), staging `X-Robots-Tag: noindex` (only if staging gets indexed).

## I. Remaining manual actions (not pretend-complete)

1. Deploy; env `SITE_URL=https://growthspareitsolutions.com`, `SECURE_SSL_REDIRECT=True`; host routes www→Django (middleware 301s to apex) and HTTP→HTTPS.
2. Search Console: add apex property (+www second), verify via DNS TXT, submit `sitemap.xml`, inspect `/`, 3 services, 3 locations, contact, consultation; request indexing (~10/day quota); monitor Pages/Enhancements (Breadcrumbs/FAQ/Article), Core Web Vitals, queries, manual actions. Full steps in `SEARCH_CONSOLE_SETUP.md`.
3. GA4: mark `audit_request_submit`, `contact_submit`, `whatsapp_click`, `phone_click` as conversions (`CONVERSION_TRACKING.md`).
4. GBP/Bing/Apple + directories per `OFFSITE_SEO_PLAN.md` + `LOCAL_SEO_AUDIT.md` (exact NAP; service areas, not fake offices).
5. Blog: publish per roadmap (2/month, fill meta/featured image/alt).

## J. Off-site requirements

See `OFFSITE_SEO_PLAN.md` (GBP → Bing/Apple → JustDial/IndiaMART/Sulekha/Clutch/GoodFirms → dev-community presence → client "Built by" links → ONE linkable asset (cost guide/checklist) → local PR → 1 guest post/quarter). No bought links, no farms, no fake reviews. Nothing claimed as built.

## K. Recommended next 30 days

- Week 1: deploy + Search Console + GA4 conversions + GBP claim + image compression.
- Week 2: publish article #1 (Delhi cost guide — highest buying intent) + expand 2 thin posts in same cluster.
- Week 3: directories phase 1 + ask 2 real clients for portfolio credit links.
- Week 4: publish article #2 (choose-a-developer) + review Search Console coverage/queries; re-crawl locally and compare.

## L. Keyword → page verification (sample; full map in SEO_KEYWORD_MAP.md)

| Keyword | Target | Intent | Title/H1/content fit | Links | CTA |
|---------|--------|--------|---------------------|-------|-----|
| website developer in Delhi / company in Delhi / designer in Delhi | `/locations/web-development-delhi/` (alias `/locations/delhi/` 301) | transactional/local | Title "…in Delhi", H1 same, Delhi-trader/clinic/startup content, in-person note | → Website Dev, SEO, AI; → restaurant/clinic/small-biz | Free Audit + WhatsApp |
| website developer in Noida | `/locations/web-development-noida/` | transactional/local | Noida startup/IT content, phased budgets | → SaaS/CRM, LMS case | same |
| website developer in Gurgaon | `/locations/web-development-gurgaon/` | transactional/local | Gurugram corporate/B2B/D2C content | → corporate, RE, D2C | same |
| web development company Delhi | `/` + Delhi location | commercial investigation | Home H1 brand + SEO hub names Delhi/Noida/Gurugram + services | hub links all | Audit/View Work |
| business website development Delhi | `/services/website-development/` + small-business industry | transactional | Service features/process/tech/pricing + use-cases; industry problem→approach | → locations + industries + Spice Garden case | Scoping session |
| SEO services Delhi | `/services/seo-optimization/` + dental SEO case | transactional | Audit→keywords→on-page→schema→GBP→reporting; honest 3–6 mo timeline | → dental case | Free SEO audit |
| AI development Delhi / chatbot | `/services/ai-whatsapp-automation/` + bot cases | transactional/educational | Cloud API + OpenAI + human handoff + limits; clinic/salon/RE/e-com uses | → 2 bot cases | Automate lead flow |

No stuffing observed (titles one primary + brand; H1s single; bodies natural). "Web design" vocabulary captured via alias (same service, no thin duplicate) — correct.

## M. Content/competitive notes (honest)

- Unsupported seed claims flagged (not rewritten without owner): "Lighthouse >95%", "workload −70%", "2x CTR", "40% auto-resolved" (services/portfolio). Recommendation: qualify ("engineered for…", "clients have seen… only with measured evidence") or attach real measurements; never invent stats.
- Testimonials correctly separate Sample vs Verified — keep; add real reviews only.
- Competitive gap (no competitor data fabricated): on-site is now on par for structure/schema/internal links; remaining gaps are **depth + proof**: real priced case studies with measured outcomes, 10 strong blog posts (vs thin 20), GBP + citations, and earned links (off-site plan). Those are month-scale, not code fixes.

## GROWTHSPARE SEO READINESS SCORE (readiness, NOT a Google ranking score)

| Pillar | Score | Basis |
|--------|-------|-------|
| Technical SEO | 92 | robots/sitemap/canonical/redirects/headers/H1/alt verified; −8 for image weight + sitemap host=request + no staging header |
| On-page SEO | 88 | unique intent-led titles/metas/H1s/breadcrumbs; −12 for remaining 70–80-char brand-suffix truncation + thin category intros |
| Local SEO | 90 | NAP consistent, HQ-vs-area wording clean, LocalBusiness justified, unique location content; −10 for GBP/citations still manual |
| Content | 68 | homepage/services/locations/industries strong + first 20 blogs deep; −32 for 20 thin posts + unverified marketing claims |
| Internal linking | 90 | hubs, footer, contextual links verified; orphan fixed; −10 for deep portfolio/blog items 2+ clicks + no related-links on some |
| Performance | 74 | preconnects/defer/dimensions/CSP/gzip-cache verified; −26 for 1 MB+ images + Play CDN + full font weights + 6 vendor libs |
| Conversion | 90 | audit/WhatsApp/tel/form/quote paths live on all commercial pages + guarded events; −10 for GA4 marking still manual |
| Authority/off-site | 35 | intentional 35: nothing built yet by design; plan exists; directories/GBP/client links pending (manual, week-scale) |
| Indexing readiness | 90 | sitemap/robots/canonical/noindex/404 verified; −10 for Search Console submission itself being manual |
| **Overall** | **80** | Mean of pillars, rounded. Was 72 at audit; +8 from forensic fixes. Content depth + images + off-site are the path to 90. |
