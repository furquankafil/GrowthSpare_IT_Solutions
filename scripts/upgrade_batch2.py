"""Upgrade batch 2 (articles 6-10 of top 10). Updates live DB by slug.
Run: python scripts/upgrade_batch2.py (from project root). Idempotent.
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from apps.blog.models import BlogPost

ARTICLES = {
"conversion-rate-optimization-cro-best-practices-for-b2b-funnels": {
"meta_title": "B2B CRO: Fix the Funnel Before Buying Traffic",
"meta_description": "B2B CRO in order: clarify offer, one CTA, cut form friction, add proof, speed up. Plus what not to test early.",
"tags": "CRO, B2B Marketing, Lead Generation",
"content": """<p><strong>Quick answer:</strong> B2B conversion optimisation beats buying more traffic because leads = traffic &times; conversion rate, and most funnels leak at fixable points: unclear offer, competing calls to action, long forms, missing proof, slow pages. Fix those in order before running a single A/B test — testing a confusing page just measures confusion precisely.</p>
<h2>Fix 1: say what happens next</h2>
<p>Most B2B pages describe the company, not the transaction. Above the fold, state the offer and the next step in one line each: "We build booking websites for clinics starting at &#8377;4,999 — get a free audit of your current site." If a visitor can't answer "what do I get and what do I click" in five seconds, nothing below the fold matters.</p>
<h2>Fix 2: one page, one primary CTA</h2>
<p>Audit pages usually beg: call, WhatsApp, form, newsletter, chatbot, social icons. Pick one primary action (for Indian SMEs, often WhatsApp or a short form) and demote the rest to quiet secondary links. Our own pages pair "Get a Free Website Audit" with a single WhatsApp alternative — two paths, one decision, no paralysis.</p>
<h2>Fix 3: cut form friction ruthlessly</h2>
<p>Every field costs enquiries. Name + phone/WhatsApp + one-line requirement converts multiples better than an eight-field "detailed brief" — collect the rest on the call. Multi-step forms (like our audit request) work because each step feels trivial; a single wall of fields feels like homework. Never ask for budget before demonstrating value; ask it after the visitor is invested.</p>
<h2>Fix 4: proof where doubt peaks</h2>
<p>Place evidence at the scroll depth where scepticism hits: portfolio pieces after the offer, process after pricing questions, FAQs at objections ("how long?", "how much?", "who owns the code?"). Genuine proof only — real projects, real process, real contact details. Fabricated logos and invented percentages convert briefly and destroy trust permanently.</p>
<h2>Fix 5: speed is a conversion feature</h2>
<p>Each second of mobile load visibly trims conversion. Compress images, defer non-critical scripts, and test the enquiry path on a mid-range Android phone — not your office fibre MacBook. If the form takes four seconds to become interactive, your copy never gets read.</p>
<h2>What NOT to test early</h2>
<p>Button colours, headline synonyms, and hero image swaps while the offer is unclear. Test big levers first (offer, CTA count, form length, proof placement), one change at a time, for at least two business cycles or a few hundred visitors — whichever is longer. Low-traffic B2B sites should test sequentially with before/after windows, not pretend to run statistically pure splits on 40 visitors a week.</p>
<h2>FAQs</h2>
<p><strong>What is a good B2B conversion rate?</strong><br>It varies wildly by traffic source and offer (2–5% of targeted visitors enquiring is a healthy band for service businesses, not a promise). Benchmark against your own past months, not internet averages.</p>
<p><strong>Should I add a chatbot or shorten the form first?</strong><br>Shorten the form — it helps 100% of visitors. Add the bot second for after-hours capture. If you'd like both diagnosed on your pages, our <a href="/services/digital-marketing/">digital marketing team</a> folds CRO into the <a href="/consultation/book/">free website audit</a>.</p>""",
},
"the-anatomy-of-a-high-converting-b2b-landing-page-in-tailwind-css": {
"meta_title": "B2B Landing Page Blueprint That Converts",
"meta_description": "Section-by-section B2B landing page blueprint: hero, proof, problem, process, offer, FAQ, final CTA — plus copy and mobile rules.",
"tags": "Landing Page, B2B, Web Design, Tailwind CSS",
"content": """<p><strong>Quick answer:</strong> a high-converting B2B landing page follows a fixed anatomy: navigation with CTA, hero stating one promise, trust strip, problem agitation, how-it-works, offer with proof, objection-handling FAQ, and a final CTA repeating the hero action. Miss any section and a slice of visitors leaves unconverted; reorder them and the argument stops flowing. The framework below works whether you build in Tailwind, plain CSS, or any stack.</p>
<h2>Section 1: navigation with one job</h2>
<p>Logo left, phone/WhatsApp visible, one CTA button right — no mega-menu. Landing traffic is rented attention; every nav link that isn't the conversion action is an exit door. Keep footers minimal on landing variants.</p>
<h2>Section 2: hero — one promise, one action</h2>
<p>Headline names the outcome ("Booking websites for clinics that fill appointment slots"), subhead names the mechanism and risk-reversal ("mobile-first builds from &#8377;4,999 with WhatsApp confirmations — free audit first"), CTA button repeats the single action, and a visual shows the product in context. Write the hero for skimmers: most visitors read 15 words before deciding to scroll or bounce.</p>
<h2>Section 3: trust strip</h2>
<p>Immediately under the hero: client types served, project count (only real numbers), technologies, or locations. This section answers "are these people legitimate?" in three seconds. Use genuine items — our pages show real service areas (Delhi, Noida, Gurugram) and real starting prices instead of invented awards.</p>
<h2>Sections 4–5: problem, then how it works</h2>
<p>Name the pain precisely ("appointments lost to phone-tag and Instagram DMs") before presenting the build — pain-first copy converts because the visitor feels understood. Then a 3–4 step process (audit → design → build → launch) that makes hiring you feel safe and finite. Abstract "solutions" without a process read as risk.</p>
<h2>Sections 6–7: offer with proof, then FAQ</h2>
<p>State scope, timeline band, and starting price plainly — hidden pricing doesn't create mystique, it creates bounces to competitors who publish ranges. Follow with an FAQ answering the real objections (cost, time, ownership, support), which doubles as search-friendly content. Close by repeating the hero CTA verbatim; new wording at the end forces re-decision.</p>
<h2>Copy and mobile rules</h2>
<ul><li><strong>One reader, one action:</strong> write to a single persona ("clinic owners in Delhi") and a single next step.</li><li><strong>Concrete over clever:</strong> "sites starting at &#8377;4,999, delivered in 2–4 weeks" beats "digital excellence unleashed."</li><li><strong>Mobile-first:</strong> thumb-reach CTA, tap-to-call/WhatsApp, forms with large inputs, no hover-dependent content — most Indian B2B research happens on phones.</li><li><strong>Tailwind notes:</strong> utility classes speed up responsive iteration (mobile: classes first, then sm:/lg: overrides); keep the class soup manageable with components for repeated cards and CTAs.</li></ul>
<h2>FAQs</h2>
<p><strong>How long should a B2B landing page be?</strong><br>As long as the argument needs — usually 6–9 sections. Short pages convert warm traffic; cold traffic needs the full proof chain. Match length to awareness, not fashion.</p>
<p><strong>Can I see this structure applied?</strong><br>Browse our <a href="/portfolio/">portfolio</a> and our <a href="/services/website-development/">website development service</a> — or send us your current page for a <a href="/consultation/book/">free audit</a> and we'll mark exactly which sections are missing.</p>""",
},
"why-proprietary-crms-outperform-off-the-shelf-saas-platforms": {
"meta_title": "Custom CRM vs SaaS: Total Cost & Fit Compared",
"meta_description": "Custom CRM vs Salesforce/HubSpot: per-seat math, workflow fit, data ownership — and when SaaS still wins. Decision table included.",
"tags": "CRM, Custom Software, SaaS",
"content": """<p><strong>Quick answer:</strong> proprietary CRMs beat off-the-shelf SaaS on total cost over a multi-year horizon and on fit to unusual workflows — you pay once for software shaped around your pipeline instead of forever per seat for software your team bends around. SaaS still wins for small teams with standard pipelines who need to start this week. The right choice depends on team size, process uniqueness, and how long you'll use it.</p>
<h2>The real math: compounding seats vs one build</h2>
<p>Take an illustrative example (your numbers will differ): 15 salespeople on a mid-tier SaaS plan at roughly &#8377;2,000/user/month costs &#8377;3.6 lakh a year — every year, rising with headcount and plan tiers. A custom CRM at our starting range of &#8377;24,999 for focused builds (larger pipelines scoped individually) plus modest hosting and maintenance crosses below the SaaS line surprisingly fast, and the gap compounds: year three of SaaS is another &#8377;3.6+ lakh, while year three of owned software is maintenance only. Run this arithmetic with your actual seat count before deciding — most teams never do.</p>
<h2>Fit: software bent around you, not you around it</h2>
<p>Generic CRMs assume a generic pipeline. Real businesses have quirks: approval chains, regional team structures, WhatsApp-first follow-ups, invoice-linked stages, Hindi/English mixed customer data. Each workaround (custom fields, third-party plugins, manual exports) adds friction and subscription add-ons. A proprietary build encodes your actual process — stages, permissions, reports, notifications — so the tool disappears into the work instead of fighting it.</p>
<h2>Ownership: data, roadmap, and exit</h2>
<p>With SaaS, your customer database lives on someone else's schema under someone else's pricing power — export formats, API limits, and price rises are their decisions. Owned software means the database, the code, and the roadmap are yours: add the report you need this week, integrate the WhatsApp flow next month, migrate hosts freely. For businesses where customer data is the asset, ownership is the argument.</p>
<h2>When SaaS still wins (honestly)</h2>
<p>Stay on SaaS if: the team is under ~5 with a standard pipeline, you need to start this week, you lack anyone to own the system, or requirements change monthly (SaaS absorbs churn better than a half-built custom tool). There is no shame in Salesforce or HubSpot — the mistake is defaulting to them for a 30-person team with a five-year horizon without running the math.</p>
<h2>Decision table</h2>
<ul><li><strong>Team &lt;5, standard sales, short horizon:</strong> SaaS.</li><li><strong>Team 5–15, some custom stages, 2+ year horizon:</strong> evaluate both; custom often wins on cost alone.</li><li><strong>Team 15+, unique workflow, regulated/valuable data:</strong> custom, usually decisively.</li><li><strong>Weird operations (distribution, multi-branch admissions, property pipelines):</strong> custom — SaaS workarounds will cost more than the build.</li></ul>
<h2>Migration path that avoids regret</h2>
<p>Spreadsheet → SaaS trial (learn what you actually need) → custom build informed by real usage. Teams that skip the middle step often over-specify; teams that stay in spreadsheets too long drown. If spreadsheets are already breaking, <a href="/consultation/book/">book a scoping call</a> — we'll map your pipeline into a <a href="/services/crm-software-development/">CRM you own</a>, a pattern we also use for <a href="/industries/real-estate-website-development/">real-estate listing pipelines</a>.</p>""",
},
"architecting-multi-tenant-saas-databases-in-postgresql": {
"meta_title": "Multi-Tenant SaaS on PostgreSQL: 3 Models",
"meta_description": "Shared rows vs schema-per-tenant vs database-per-tenant in PostgreSQL: tradeoffs, Django specifics, classic mistakes, vendor questions.",
"tags": "SaaS, PostgreSQL, Django, Architecture",
"content": """<p><strong>Quick answer:</strong> most B2B SaaS products should start with shared tables plus a <code>tenant_id</code> column guarded by tests and (ideally) PostgreSQL Row-Level Security, move to schema-per-tenant when compliance or per-tenant operations demand it, and reserve database-per-tenant for enterprise isolation contracts. The wrong choice early is survivable; the wrong choice after 200 tenants is a migration project. Decide on isolation needs, not fashion.</p>
<h2>Model 1: shared database, shared schema (tenant_id)</h2>
<p>Every row carries its tenant; every query filters by it. Cheapest to build, operate, and back up; onboarding a tenant is one INSERT. The risk is cross-tenant leakage from a single missed filter — mitigate with a mandatory tenant scope in the ORM layer, RLS policies as a second lock, and tests that specifically attempt cross-tenant reads. Right for: most startups, internal tools, CRMs, school/clinic systems.</p>
<h2>Model 2: shared database, schema per tenant</h2>
<p>Each tenant gets its own PostgreSQL schema with identical tables. Stronger isolation, per-tenant migrations and restores, but schema-count scaling pain (migrations across 500 schemas are slow), harder cross-tenant analytics, and connection-pool pressure. Right for: regulated clients, tenants demanding data separation, white-label products with divergent schemas.</p>
<h2>Model 3: database per tenant</h2>
<p>Maximum isolation — separate backups, credentials, even versions per tenant — at maximum operational cost: provisioning automation, per-DB migrations, monitoring sprawl. Right for: enterprise contracts that require it, or tenants big enough to fund their own infrastructure. Wrong for: a 30-customer startup that just likes the sound of it.</p>
<h2>Django specifics</h2>
<p>Resolve the tenant in middleware (subdomain, header, or authenticated org), store it on the request/thread-local, and enforce it in a custom manager so bare <code>Model.objects.all()</code> can never leak. For schema-per-tenant, use <code>search_path</code> switching with disciplined migrations. For RLS, set the tenant via session variables in the same transaction. Whichever model: tenant-aware fixtures, tenant-scoped admin, and backup/restore drills per isolation unit.</p>
<h2>The mistakes that hurt later</h2>
<ul><li><strong>Unscoped queries in background tasks</strong> (Celery has no request — pass tenant explicitly).</li><li><strong>Noisy neighbours:</strong> one tenant's report query starving others — statement timeouts and read replicas.</li><li><strong>Analytics afterthought:</strong> cross-tenant reporting on schema-per-tenant requires ETL you didn't budget.</li><li><strong>Restore granularity:</strong> "restore tenant X to Tuesday" is trivial per-schema/DB and painful in shared-schema without point-in-time tooling.</li></ul>
<h2>Questions to ask any vendor</h2>
<p>Which model and why for our tenant count? Show me the tenant-isolation tests. How do you restore one tenant? How do migrations run across tenants, and how long do they take at 10× our size? Vague answers here predict outages later. If you're scoping a product now, our <a href="/services/custom-software-engineering/">engineering team</a> answers these in writing before we build — <a href="/consultation/book/">start with a scoping session</a>, especially for CRM-style products like our <a href="/services/crm-software-development/">custom CRM builds</a>.</p>""",
},
"meta-conversions-api-capi-integration-guide-for-high-roi-ad-spend": {
"meta_title": "Meta CAPI Guide: Fix Ad Tracking in 2026",
"meta_description": "When pixel data under-reports: how Meta CAPI works, server events, deduplication, event quality, testing — and its honest limits.",
"tags": "Meta Ads, CAPI, Conversion Tracking",
"content": """<p><strong>Quick answer:</strong> the Meta Conversions API (CAPI) sends conversion events from your server instead of (or alongside) the browser pixel, recovering signal lost to ad-blockers, Safari ITP, and iOS opt-outs. Implement it with shared <code>event_id</code>s so Meta deduplicates server + browser events, prioritise event quality (value, currency, hashed user data), and validate in Test Events before judging results. Expect better attribution — not magically cheaper leads.</p>
<h2>Why the pixel alone under-reports now</h2>
<p>Three forces erode browser tracking: content blockers that never load the pixel, Safari/Firefox caps on cookie lifetimes, and iOS prompts where most users decline tracking. The symptom is familiar — "Meta shows 10 leads, our CRM shows 25" — and the business damage is misattributed: winning audiences get killed because their conversions were invisible. Server events bypass the browser entirely, restoring the missing rows.</p>
<h2>How CAPI + Pixel work together</h2>
<p>Send both, deduplicated: browser pixel fires instantly for UX-speed events; your server sends the authoritative record (especially offline/WhatsApp-closed sales the pixel can never see). Matching <code>event_id</code> + <code>event_name</code> lets Meta merge the pair instead of double-counting. Never run server-only without reason — you lose the pixel's rich browser context (URL, referrer, micro-interactions).</p>
<h2>Implementation paths</h2>
<ul><li><strong>Partner integration</strong> (fastest): e-commerce/CRM platforms with native CAPI connectors — configure, map events, done in hours. Right for standard stores.</li><li><strong>Gateway/API custom</strong> (flexible): a Django endpoint captures your conversion (form submit, WhatsApp qualification, payment webhook), hashes user data server-side, and posts to Meta's events endpoint. Right for custom funnels, lead-gen sites, and offline closes — exactly the setups where the pixel is weakest.</li></ul>
<h2>Event quality decides the payoff</h2>
<p>CAPI with bare event names barely helps. Include value + currency on every purchase/lead event, hash and send available customer parameters (email, phone, name, city), keep event naming consistent with the pixel, and send funnel stages (ViewContent → Lead → Purchase) so the algorithm learns progression, not just endpoints. In Events Manager, the Event Match Quality score tells you plainly how much signal Meta can actually use — chase it above "good" before judging ROAS movement.</p>
<h2>Testing and honest limits</h2>
<p>Validate with Test Events (send, watch it arrive with parameters), then compare Ads Manager vs CRM counts over two full weeks — attribution windows lag. And be clear-eyed: CAPI fixes measurement, not fundamentals. If the offer is weak or the landing page leaks (see our <a href="/blog/conversion-rate-optimization-cro-best-practices-for-b2b-funnels/">CRO guide</a>), perfect tracking just measures the leak accurately. Fix the funnel first, then the signal.</p>
<h2>FAQs</h2>
<p><strong>Does CAPI replace the Pixel?</strong><br>No — run both with deduplication. Pixel contributes browser context; CAPI contributes completeness (ad-blocked users, iOS opt-outs, offline/WhatsApp closes).</p>
<p><strong>Is server-side tracking privacy-compliant?</strong><br>It must follow the same consent rules as any tracking: disclose it in your <a href="/privacy-policy/">privacy policy</a>, honour opt-outs, hash personal data, and check current Meta + Indian regulatory guidance with your counsel. If tracking setup feels fragile, our <a href="/services/digital-marketing/">marketing team</a> reviews it inside the <a href="/consultation/book/">free audit</a>.</p>""",
},
}
for slug, a in ARTICLES.items():
    p = BlogPost.objects.get(slug=slug)
    p.content = a["content"]
    p.meta_title = a["meta_title"]
    p.meta_description = a["meta_description"]
    p.tags = a["tags"]
    p.save(update_fields=["content", "meta_title", "meta_description", "tags", "reading_time"])
    print(f"updated {slug}: {len(a['content'].split())} words")
