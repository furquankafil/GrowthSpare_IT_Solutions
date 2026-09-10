# Performance Image Audit — GrowthSpare IT Solutions

**Date:** 2026-09-09 · **Method:** Pillow inspection + template usage mapping + live HTTP checks. Originals backed up to temp (`img_backup/`) before any change; all optimized files verified served (200, correct MIME) and pages re-rendered (200, no layout changes — CSS display sizes untouched).

## Per-asset findings

| Asset | True dims (before → after) | Size before → after | Displayed at | Above fold? | Action taken |
|-------|----------------------------|---------------------|--------------|-------------|--------------|
| `static/images/logo.png` (RGB, no alpha) | 1536×1024 → **768×512** (same 3:2 aspect, LANCZOS) | 1,070,369 → **255,205 B (−76%)** | navbar h74–92px (~138px wide at new aspect); footer h56–66px; about h-10; loader h-8 | Navbar: yes (eager) | Resized to 768w (≈5× displayed — crisp on retina), `optimize=True`; added `logo.webp` (12,886 B, q82) served first via `<picture>` in navbar/footer/about; PNG fallback kept (same path, so OG image + emails + admin/login unaffected). `width`/`height` corrected to true 768×512 (previous 220×92 / 160×66 did not match file aspect). Navbar keeps `fetchpriority="high"` + eager; rest lazy |
| `static/images/founder.png` (RGB photo) | 1102×1427 → **640×829** (same aspect) | 1,944,987 → **661,118 B (−66%)** | contact circle 112px; about card ≤400px wide | No | Resized to 640w (1.6× largest display), optimized; added `founder.webp` (35,416 B, q80) via `<picture>` on contact + about; PNG fallback kept. `width`/`height` 640×829 added; `loading="lazy"` + `decoding="async"`; alt improved to name + role (was generic / template var) |
| `static/images/favicon.ico` | multi-size → **16/32/48 ICO** (same artwork, re-encoded) | 937,904 → **6,648 B (−99.3%)** | browser tab | n/a | Re-encoded existing art at standard icon sizes (old file was ~916 KB of uncompressed frames). Verified reloads as valid ICO + served as `image/x-icon` via `/favicon.ico` redirect |
| Client logos (`clients/*.svg`) | vector, 569–1,035 B each | unchanged (already optimal) | 120–130px cards, lazy | No | None needed |
| Portfolio/blog featured images | Unsplash hotlinks (`images.unsplash.com … w=800&q=80`) | external, not measurable locally | aspect-video cards, `loading="lazy"` already | No | **Not recompressed** (no local control). Noted as future work: download top 6 case-study images to `media/`, serve responsive sizes locally (manual; preserves Unsplash licensing checks) |
| Hero/backgrounds | none (CSS gradients + blur divs) | 0 B images | — | — | Nothing to do; gradients cost no image bytes (GPU blur cost only, acceptable) |

**Totals (local, worst case PNG path):** ~3.95 MB → ~0.92 MB (**−77%**, −3.0 MB). **Typical path (WebP first):** logo 13 KB + founder 35 KB + favicon 7 KB ≈ **55 KB** for all brand imagery (−98.6% vs original).

## What was deliberately NOT done

- No JPEG conversion of founder PNG (would change URL/format; WebP already covers modern browsers; PNG fallback retained for OG/social compatibility).
- No regeneration from `generate_assets.py` (its text rendering would alter the current official logo appearance; current file treated as canonical artwork).
- No transparency changes (both files are RGB — no alpha to preserve/break; verified `mode=RGB` before and after).
- No `srcset` size ladders beyond WebP/PNG pair: display sizes are fixed small (≤276px logo, ≤400px founder); a 768/640px file + WebP already oversupplies retina without extra variants or markup complexity.
- External Unsplash images untouched (hotlink licensing + no local copies to control).

## Verification

- `manage.py check`: clean. `/static/images/logo.png|webp|founder.png|webp` → 200 with `image/png` / `image/webp`; `/static/images/favicon.ico` → 200 `image/x-icon`.
- `/`, `/about-us/`, `/contact/` → 200 after `<picture>` edits; display classes unchanged (`h-[74px]`, `h-8`, `w-28`, `aspect-[4/5]`), so desktop/mobile appearance and CLS behavior are preserved or improved (correct intrinsic aspect now).
- Alt coverage unchanged (0 missing); founder alts improved (name + role, still factual).
- OG/Twitter default (`/static/images/logo.png`) still resolves — now 76% smaller for link-preview crawlers too.
