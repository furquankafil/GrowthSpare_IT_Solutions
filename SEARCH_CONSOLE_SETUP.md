# Search Console Setup — GrowthSpare IT Solutions

Nothing has been submitted automatically — Search Console requires a human with Google access. Do this after deployment.

## 1. Prerequisites

- Production deploy live at `https://growthspareitsolutions.com` with HTTPS.
- `SITE_URL=https://growthspareitsolutions.com` in production env.
- Verify these URLs return 200 with correct content:
  - `https://growthspareitsolutions.com/robots.txt` (must list `Sitemap: https://growthspareitsolutions.com/sitemap.xml`, must NOT disallow `/consultation/book/`)
  - `https://growthspareitsolutions.com/sitemap.xml` (index of static/services/categories/portfolio/blogs)

## 2. Add property

1. Go to Google Search Console → Add property → **URL prefix**: `https://growthspareitsolutions.com` (and add `https://www.growthspareitsolutions.com` as a second property if www serves traffic).
2. Verify ownership via **HTML tag** (paste into `templates/base.html` `extra_head` on homepage temporarily) or **DNS TXT** (preferred — no code change).

## 3. Submit sitemap

1. Sitemaps → Add new sitemap → enter `sitemap.xml` → Submit.
2. Expect: "Success — discovered URLs" within 24–48h. If "Submitted URL blocked by robots.txt" appears, re-check `robots.txt` (fixed in this release: consultation is now allowed; `?q`/`?category`/`?page` are disallowed).

## 4. Request indexing (priority order)

1. `/` (homepage)
2. `/services/website-development/`, `/services/seo-optimization/`, `/services/ai-whatsapp-automation/`
3. `/locations/web-development-delhi/`, `/locations/`, `/locations/web-development-noida/`, `/locations/web-development-gurgaon/`
4. `/industries/`, top 3 industry pages
5. `/contact/`, `/consultation/book/`
6. Use URL Inspection → Request Indexing for each (quota ~10/day).

## 5. Configure

- **Settings → Crawl stats:** monitor for 5xx spikes after deploy.
- **Pages report:** target 0 "Blocked by robots", 0 accidental "Excluded by noindex" on commercial pages. Expected `noindex`: 404 page only; `?q=`/`?category=` filtered pages (by design).
- **Enhancements:** validate Breadcrumbs, FAQ, Article rich results after 1–2 weeks.
- **Links:** check Top linked pages — homepage, Website Development, Delhi location should lead.
- **Removals:** only if staging subdomain got indexed — add Removals + ensure staging sends `X-Robots-Tag: noindex` or is password-protected.

## 6. Domain/canonical checklist

- [ ] `http://` → `https://` redirect active (host-level; see FINAL report manual steps)
- [ ] `www` vs apex: pick ONE canonical (recommend apex `growthspareitsolutions.com`), redirect the other with 301 at Nginx/host level
- [ ] Trailing-slash consistency: Django APPEND_SLASH handles; canonicals always include trailing slash
- [ ] Canonical tag on every page points to `SITE_URL` + path (never staging host)
- [ ] Sitemap URLs use canonical host only

## 7. Ongoing (monthly)

- Review Performance → Queries: which commercial/local terms surface; feed winners into CONTENT_STRATEGY.md.
- Review Pages → "Crawled - currently not indexed" for thin content to improve (never doorway).
- Re-submit sitemap only after structural URL changes.
