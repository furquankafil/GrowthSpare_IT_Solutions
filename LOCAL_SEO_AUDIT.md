# Local SEO Audit — GrowthSpare IT Solutions

**Source of truth:** `apps/core/context_processors.py` (`OFFICIAL_PHONE +91 9811579273`, `OFFICIAL_EMAIL growthspareitsolution@gmail.com`, `OFFICIAL_LOCATION` from `OFFICIAL_LOCATION_ADDRESS` env default `D-50, Shaheen Bagh, Okhla, New Delhi – 110025, India`) + contact page + schema. Crawled 2026-09-09.

## NAP consistency — PASS

| Surface | Name | Phone | Email | Address | Evidence |
|---------|------|-------|-------|---------|----------|
| Homepage (footer + schema) | GrowthSpare IT Solutions | +91 9811579273 | growthspareitsolution@gmail.com | D-50, Shaheen Bagh, Okhla, New Delhi 110025 | footer `OFFICIAL_*` vars; `LocalBusiness` JSON-LD |
| Contact page (visible + schema) | same | same (`tel:` + WhatsApp `wa.me/919811579273`) | same (`mailto:`) | same + map embed `GOOGLE_MAPS_EMBED_QUERY` | `contact_form.html`, `contact/views.py` schema |
| Location pages (Delhi/Noida/Gurgaon) | same | same (footer/global) | same | Delhi page states Okhla HQ; Noida/Gurgaon state service-area, **not** offices | `LOCATION_DATA` intros; no office claim strings found |
| Footer | same | same | same | same | `footer.html` |
| Schema (home/contact/locations) | same | same | same | PostalAddress Shaheen Bagh/Okhla/New Delhi/110025/IN, hours Mon–Sat 09:00–19:00 | `_company_local_business_schema()` shared helper |

No mismatched phone/email/address variants found. `wa.me/919811579273` is digits-only form of the same number (required by wa.me) — not an inconsistency.

## Physical office vs service area — PASS (wording verified)

- Delhi page: "headquartered in Okhla, Delhi… in-person meetings are straightforward" — claims HQ (matches contact address). OK.
- Noida page: "Noida's proximity to Delhi means the same in-person availability applies… straightforward to arrange" — availability, **not** an office. OK.
- Gurgaon page: no office claim; "corporate-facing" positioning only. OK.
- `/locations/` hub: "based in Okhla, New Delhi and serves… Delhi, Noida and Gurugram" — explicit HQ-vs-serves distinction. OK.
- Homepage: "Based in New Delhi", "Delhi, Noida & Gurugram" as served areas; automated scan confirms no `office in Noida/Gurgaon`, `our Noida office` strings. OK.
- `areaServed: ["New Delhi","Noida","Gurugram"]` on LocalBusiness — correct service-area usage, not fake branches.

**Conclusion:** No fake physical location implied. Do not add Noida/Gurgaon street addresses, map pins, or GBP locations unless real offices open.

## LocalBusiness schema appropriateness — APPROPRIATE

- Used on: home, contact, 3 location pages. All share one NAP/hours helper (consistent). Business is a local-serving IT firm with a real address + phone + hours on the contact page — LocalBusiness is justified.
- Not used on: blog posts, portfolio, legal pages (correct).
- `sameAs`: only LinkedIn/Instagram/Facebook URLs already linked in footer (verified in `footer.html`) — nothing invented. GitHub link in footer is intentionally excluded from schema (personal vs company). Good.
- Hours Mon–Sat 09:00–19:00 match contact page "Monday - Saturday: 9:00 AM - 7:00 PM IST". Good.

## Location page uniqueness — PASS (not doorway)

- Delhi (525w): Old Delhi/Karol Bagh traders, South/Central startups, WhatsApp/walk-in/referral scoping, Delhi in-person.
- Noida (502w): Sector 62/16 coworking, Expressway IT/ITES, tech-literate bar, handoff-ready code, phased startup budgets.
- Gurgaon (497w): Cyber City/MG Road/Golf Course Road, B2B/investor-facing credibility, D2C/real-estate mobile focus.
- Distinct services_focus + FAQs per city (verified in `views.py LOCATION_DATA`). Short aliases (`/locations/delhi/` etc.) are 301s, not duplicate renders. No city-swap pages.

## Google Business Profile — NOT claimed (correct to document as manual)

Do NOT fabricate. Manual steps for owner:
1. Create/claim ONE profile: name `GrowthSpare IT Solutions`, address exactly `D-50, Shaheen Bagh, Okhla, New Delhi – 110025, India`, phone `+91 9811579273`, site `https://growthspareitsolutions.com`, hours Mon–Sat 09:00–19:00.
2. Categories: Website designer / Software company / Internet marketing service (pick closest primary + 2 secondaries; don't stuff).
3. Service areas: Delhi, Noida, Gurugram (service-area, not extra addresses).
4. Link `/contact/` NAP must stay character-identical to GBP.
5. No map embed beyond the existing contact-page iframe (real location only). No review solicitation schemes; respond to real reviews only.
