# Conversion Tracking — GrowthSpare IT Solutions

**Status:** Implemented client-side (privacy-friendly, no extra cookies). GA4 pageview already present (`G-P68BKJ57R4` in `templates/base.html`). Event layer added in `static/js/conversion_tracking.js` (loaded `defer` in base).

## Events tracked (GA4 → Reports → Engagement → Events)

| Event | Trigger | Code |
|-------|---------|------|
| `whatsapp_click` | Any `wa.me/` link (sticky button, hero, location/industry CTAs, footer) | `conversion_tracking.js: bindWhatsApp()` — params: `link_label`, `page_path` |
| `phone_click` | Any `tel:` link | `bindTelMail()` — `page_path` |
| `email_click` | Any `mailto:` link | `bindTelMail()` — `page_path` |
| `audit_request_submit` | Consultation multi-step form submit (`#scoping-multi-step-form`) | `bindForms()` — `page_path` |
| `contact_submit` | Contact form submit (`/contact/`) | `bindForms()` — `page_path` |
| `newsletter_submit` | Footer newsletter submit | `bindForms()` — `page_path` |
| `portfolio_click` | Any `/portfolio/` link click (secondary CTA "View Our Work") | `bindPortfolio()` — `link_label`, `page_path` |

All events guard `typeof window.gtag === "function"` and never block navigation.

## GA4 manual steps (MANUAL ACTION REQUIRED)

1. GA4 Admin → Events → **Mark as conversion**: `audit_request_submit`, `contact_submit`, `whatsapp_click`, `phone_click` (newsletter/portfolio stay observational).
2. Reports → Attribution → Conversion paths: verify audit requests attribute to `/`, locations, services, blog.
3. If moving to Google Tag Manager later, these `gtag("event", …)` calls work unchanged.

## CSP note

`config/settings/base.py` CONTENT_SECURITY_POLICY now allows `https://www.googletagmanager.com` (script) and `https://www.google-analytics.com` + `region1` (connect). Without this, GA4 was silently blocked by CSP. Verified against `templates/base.html` script sources.

## What was NOT added (deliberately)

- No Meta Pixel, no Hotjar, no session replay — invasive and unnecessary at this stage.
- No server-side purchase/value tracking — lead-gen site; form submits are the conversion.
- No PII in event params (no email/phone/name sent to GA4).
