"""Upgrade batch 1 (articles 1-5 of top 10). Updates live DB by slug.
Run: python scripts/upgrade_batch1.py (from project root). Idempotent.
"""
import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()
from apps.blog.models import BlogPost

ARTICLES = {
"how-to-securely-connect-whatsapp-cloud-api-with-django-webhooks": {
"meta_title": "WhatsApp Cloud API + Django: Secure Webhook Guide",
"meta_description": "Connect WhatsApp Cloud API to Django securely: webhook verification, signature checks, 24-hour rules, queues and human handoff.",
"tags": "WhatsApp Cloud API, Django, Webhooks, Automation",
"content": """<p><strong>Quick answer:</strong> connecting the WhatsApp Cloud API to Django means exposing a webhook endpoint that Meta calls for incoming messages and delivery statuses. The work that matters is not the endpoint itself but doing it securely: verifying the webhook, validating every request signature, replying inside WhatsApp's 24-hour customer-service window, and processing messages in a background queue so the webhook never blocks. Get those four right and you have a reliable automation foundation; skip them and you get silent message loss.</p>
<h2>Prerequisites before writing code</h2>
<p>You need a Meta developer app with the WhatsApp product added, a phone number (use Meta's free test number while developing), a permanent access token stored as an environment variable — never in source code — and the phone number ID, which is different from the displayed phone number. On the Django side you need an HTTPS public URL; Meta will not call webhooks over plain HTTP, so develop with a tunnel and deploy behind TLS.</p>
<h2>Step 1: the verification handshake</h2>
<p>When you register the webhook URL in the Meta dashboard, Meta sends a GET request with <code>hub.mode=subscribe</code>, a <code>hub.verify_token</code> you chose, and a <code>hub.challenge</code>. Your view must check that the mode is <code>subscribe</code> and the token matches your stored secret, then return the challenge string verbatim. This trips up first-timers because the endpoint must answer GET (verification) and POST (events) on the same URL — route both methods explicitly and keep the verification branch tiny.</p>
<h2>Step 2: validate every incoming request signature</h2>
<p>Meta signs each POST with an HMAC-SHA256 signature in the <code>X-Hub-Signature-256</code> header, computed with your app secret. Recompute it over the raw request body and compare with a constant-time comparison. Reject mismatches with a 403 before parsing anything. This is the single most-skipped step in tutorials, and skipping it means anyone who discovers your webhook URL can inject fake customer messages into your system.</p>
<h2>Step 3: understand the 24-hour rule</h2>
<p>WhatsApp lets businesses reply freely for 24 hours after a customer's last message (the customer-service window). Outside it, only pre-approved template messages go through. Your system must track per-conversation window state: inside the window, send free-form replies; outside it, send a template or wait for the customer to re-engage. Design your appointment reminders and follow-ups around this rule instead of discovering it after launch.</p>
<h2>Step 4: never process inside the webhook</h2>
<p>Meta expects a fast 200 response and retries aggressively on timeouts — slow processing causes duplicate deliveries. The correct pattern is: validate signature, enqueue the payload ID in Celery/Redis, return 200 immediately, then do the slow work (AI replies, CRM writes, confirmations) in the worker. Make handlers idempotent by tracking processed message IDs so a retried delivery never double-books an appointment or double-charges a flow.</p>
<h2>Common failures and fixes</h2>
<ul><li><strong>Verification fails:</strong> token mismatch or the GET branch returns JSON instead of the raw challenge string.</li><li><strong>Messages arrive but replies fail:</strong> expired token (use a permanent token, rotate on a schedule) or messaging outside the 24-hour window without a template.</li><li><strong>Duplicate actions:</strong> slow webhook responses triggering Meta retries — move work to the queue and dedupe by message ID.</li><li><strong>Echo loops:</strong> your own outgoing messages re-triggering handlers — filter by message direction/status before processing.</li></ul>
<h2>Build in the human handoff from day one</h2>
<p>Automation should handle the routine — timings, prices, booking, FAQs — and hand over the moment confidence drops or the customer asks for a person. Route the full conversation transcript to your team over WhatsApp or email so the human continues seamlessly. For a clinic or salon, that handoff is the difference between automation that books appointments and automation that loses patients.</p>
<h2>FAQs</h2>
<p><strong>Is the WhatsApp Cloud API free?</strong><br>Meta provides free access tiers and conversation-based pricing that changes by market and category; check current Meta pricing for India before budgeting. Our <a href="/services/ai-whatsapp-automation/">AI and WhatsApp automation service</a> starts at &#8377;7,999 for the build itself.</p>
<p><strong>Can I use my existing business number?</strong><br>Yes, you can migrate a number to the Cloud API, but migration disables the WhatsApp Business app on that number — plan the cutover so you never miss customer messages mid-move.</p>
<h2>Want this built instead of DIY?</h2>
<p>If webhooks, queues, and template approvals sound like weeks you don't have, <a href="/consultation/book/">get a free website audit</a> and mention WhatsApp automation — we scope appointment booking, lead qualification, and support bots for businesses like <a href="/industries/clinic-website-development/">clinics</a>, including the human handoff, from &#8377;7,999.</p>""",
},
"unlocking-b2b-conversions-the-power-of-conversational-ai-chatbots": {
"meta_title": "AI Chatbots for B2B: Where They Convert (and Don't)",
"meta_description": "Where AI chatbots lift B2B conversions: qualification, after-hours capture, instant answers — plus honest limits and a converting bot blueprint.",
"tags": "AI Chatbot, B2B, Lead Generation, WhatsApp",
"content": """<p><strong>Quick answer:</strong> conversational AI chatbots lift B2B conversions in exactly three places: instant answers to repeat questions, after-hours lead capture, and structured qualification before a human calls. They fail at complex negotiation, upset customers, and anything requiring judgment. A chatbot that does the first three and hands off the rest will outperform a contact form; a chatbot positioned as a replacement for your sales team will disappoint.</p>
<h2>Where chatbots actually earn their keep</h2>
<p>Most B2B enquiries arrive with the same five questions — pricing ballpark, timelines, scope fit, location coverage, next step. Answering those in 30 seconds instead of next business day wins deals, especially for Indian buyers who message late evening. The chatbot's job is to compress that first response from hours to seconds and to collect the three facts a salesperson needs: what they want, their budget band, and how to reach them.</p>
<h2>Anatomy of a bot that converts</h2>
<ul><li><strong>A greeting with a menu, not an open void.</strong> "Hi! I can share pricing, timelines, or book a call — which helps most?" beats "How can I help?" because it teaches the visitor what the bot does well.</li><li><strong>Three-question qualification max.</strong> Need, timeline, contact detail. Every extra question leaks leads; collect the minimum and let the human call do the rest.</li><li><strong>One proof point early.</strong> A line about who you serve ("we build sites for clinics, restaurants, and local businesses across Delhi NCR") builds more trust than any animation.</li><li><strong>An explicit human exit.</strong> "Want me to have someone call you tomorrow at 11?" converts the hesitant and rescues confused conversations.</li></ul>
<h2>Example: a consulting enquiry flow</h2>
<p>Visitor: "How much for a website?" Bot: "For most small businesses our sites start at &#8377;4,999 — the exact figure depends on pages and features. Are you looking for a simple business site, online ordering/bookings, or something custom?" Visitor picks "bookings." Bot: "Got it — clinics and salons usually need a booking flow with WhatsApp confirmations. What's the best number for a 10-minute scoping call?" Three turns, qualified lead, zero staff time. That flow pattern works for <a href="/industries/real-estate-website-development/">real-estate enquiry qualification</a> and service businesses alike.</p>
<h2>Website chat vs WhatsApp bot</h2>
<p>Website chat catches visitors mid-browse; WhatsApp bots continue the conversation where Indian customers actually reply. The strongest setup is both sharing one brain: qualify on the site, continue on WhatsApp, confirm over a call. Our <a href="/services/ai-whatsapp-automation/">AI and WhatsApp automation builds</a> work this way, on the official Cloud API with human handoff included.</p>
<h2>Measure three numbers, ignore the rest</h2>
<p>Lead rate (conversations that yield contact details), handoff rate (share needing a human — 20–40% is healthy, not failure), and first-response time (seconds, always). Containment rate alone is a vanity metric: a bot that "contains" 95% by stonewalling visitors is destroying enquiries.</p>
<h2>FAQs</h2>
<p><strong>Will a chatbot annoy my serious buyers?</strong><br>Only if it blocks the human path. Keep a visible "talk to a person" option and a phone number alongside the bot, and serious buyers treat it as a fast lane, not a wall.</p>
<p><strong>How much does a business chatbot cost?</strong><br>It depends on integrations (booking, CRM, payments add scope). Our WhatsApp automation builds start at &#8377;7,999 — <a href="/consultation/book/">ask for a free audit</a> describing the one workflow costing you the most manual hours, and we'll scope exactly that.</p>""",
},
"how-to-securely-integrate-openai-gpt-4o-into-your-erp-workflows": {
"meta_title": "Using GPT-4o in ERP Workflows, Securely",
"meta_description": "Add GPT-4o to ERP workflows safely: right first use-cases, API proxy design, cost control, evaluation loops and a data-security checklist.",
"tags": "OpenAI, GPT-4o, ERP, AI Automation",
"content": """<p><strong>Quick answer:</strong> the safe way to put GPT-4o inside ERP workflows is through a server-side proxy that holds the API key, strips or redacts sensitive fields before prompting, and keeps a human in the loop on anything consequential. Start with one low-risk workflow (drafting, summarising, classifying), measure it against a small test set, then expand. Most failed AI pilots fail on data handling and evaluation — not on model quality.</p>
<h2>Start with workflows where mistakes are cheap</h2>
<p>Good first candidates: drafting customer replies for human approval, summarising long order/support threads, classifying tickets or leads into categories, extracting structured fields (dates, amounts, names) from documents. Bad first candidates: unsupervised credit decisions, auto-sending messages to customers, anything touching payroll or compliance filings. The rule: AI proposes, humans dispose — until a workflow has months of measured accuracy behind it.</p>
<h2>The architecture that keeps you safe</h2>
<p>Never call OpenAI from the browser or embed keys in client apps. Route all calls through your backend (Django/ERP middleware), which authenticates the user, checks permissions on the record being processed, redacts fields the model doesn't need (bank details, full addresses, personal IDs), logs every call with its input hash and output, and enforces per-user rate limits. That proxy is also where you swap models later without touching every workflow.</p>
<h2>Control cost before it surprises you</h2>
<p>LLM spend scales with tokens × calls, so design for it: use the smallest capable model per task, cache repeated classifications, batch overnight summarisation instead of real-time, and truncate context to the relevant excerpt rather than entire records. Set billing alerts from week one — a runaway loop calling GPT-4o per row of a 50,000-row table is the classic first-month accident.</p>
<h2>Evaluate like an engineer, not a demo audience</h2>
<p>Collect 50–100 real examples of each task, label the correct outputs, and run every prompt change against that set before deploying. Track accuracy plus the cost per task. Keep a human-review queue for low-confidence outputs (ask the model to return a confidence signal or route by rule), and review a sample weekly even after launch — data drifts, and prompts rot.</p>
<h2>Data-security checklist</h2>
<ul><li><strong>Know your data flow:</strong> which fields leave your server, to which endpoint, under which agreement (API data-usage terms differ from consumer chat terms).</li><li><strong>Minimise by default:</strong> send excerpts, not records; mask PII with placeholders before prompting.</li><li><strong>Retain logs wisely:</strong> keep hashes and metadata for audit; avoid storing raw customer text alongside model outputs indefinitely.</li><li><strong>Access control:</strong> AI features respect the same role permissions as the ERP screens they augment.</li><li><strong>Exit plan:</strong> abstract the provider call so a policy change means config, not surgery.</li></ul>
<h2>Rollout order that works</h2>
<p>One pilot workflow with a named owner → 4 weeks measured → expand to adjacent workflows → only then consider customer-facing automation. Teams that follow this order get compounding wins; teams that connect five workflows in week one get five unmeasured risks.</p>
<h2>FAQs</h2>
<p><strong>Will AI replace our ERP?</strong><br>No — it makes the ERP you have more valuable by removing drafting, triage, and summarisation labour around it. Replacement projects fail far more often than augmentation ones.</p>
<p><strong>What does a pilot cost?</strong><br>A single scoped pilot (one workflow, proxy, evaluation set) is a small custom build. <a href="/consultation/book/">Book a scoping session</a> describing the workflow eating your team's hours — our <a href="/services/custom-software-engineering/">engineering team</a> will tell you honestly whether AI fits it or whether plain automation is cheaper.</p>""",
},
"technical-seo-checklist-for-sub-300ms-django-page-speeds": {
"meta_title": "Django Speed Checklist: Lower TTFB, LCP & CLS",
"meta_description": "Speed up Django sites: measure first, fix server response, compress assets, defer JS, optimise fonts and images — practical checklist.",
"tags": "Django, Page Speed, Core Web Vitals, Technical SEO",
"content": """<p><strong>Quick answer:</strong> fast Django pages come from four layers in order: quick server response (queries, caching), small compressed assets, non-blocking JavaScript and fonts, and right-sized images. Measure with PageSpeed Insights and Search Console's Core Web Vitals report first — optimising without measuring means tuning the wrong layer. Most business sites we see lose their speed budget to unoptimized images and render-blocking scripts, not to Django itself.</p>
<h2>Step 0: measure the right thing</h2>
<p>Run the URL through PageSpeed Insights (mobile first) and note LCP, INP, and CLS separately — each has different fixes. Check Search Console's Core Web Vitals for the site-wide pattern: one slow template (often the homepage or a listing page) usually drags the whole average. Record the numbers before changing anything; otherwise you cannot tell which fix worked.</p>
<h2>Layer 1: server response (TTFB)</h2>
<p>Django-specific wins: kill N+1 queries with <code>select_related</code>/<code>prefetch_related</code> (the single most common Django slowdown), add DB indexes on filtered/ordered columns, cache expensive fragments and querysets in Redis, keep Gunicorn workers matched to CPU, and compress responses (WhiteNoise + Brotli/Gzip). A page doing 200 queries will never feel fast no matter how pretty the frontend is.</p>
<h2>Layer 2: asset weight</h2>
<p>Serve one minified CSS/JS path, enable Brotli at the proxy, and audit images ruthlessly — on our own site, resizing the logo from 1536px to display-appropriate 768px cut 76% of its bytes, and re-encoding the favicon properly cut 99%. Apply the same method to every template image: resize to a small multiple of displayed size, serve WebP with a PNG/JPEG fallback, and add explicit width/height to kill layout shift.</p>
<h2>Layer 3: render-blocking JS, fonts, and third parties</h2>
<p>Defer every script that isn't needed for first paint, preconnect to CDN origins you actually use, subset font weights (loading eight weights of two families is a classic self-inflicted wound), and question each third-party tag: chat widgets, heatmaps, and pixels each tax INP. Our rule: every tag must justify itself against a conversion it measurably supports.</p>
<h2>The checklist (in priority order)</h2>
<ul><li><strong>Today:</strong> compress + resize all template images; add width/height; enable text compression; defer non-critical JS.</li><li><strong>This week:</strong> fix N+1 queries; add missing DB indexes; fragment-cache the slowest view; subset fonts.</li><li><strong>This month:</strong> Redis object caching; CDN for static/media; remove or lazy-load one heavy third-party script; re-measure and compare.</li></ul>
<h2>When tuning isn't enough</h2>
<p>If the stack is a page-builder with 40 plugins or a theme loading five sliders, tuning buys 20% and a focused rebuild buys 70%. Signs you need the rebuild: template count in triple digits, no one knows what half the plugins do, or mobile PageSpeed stuck red after the checklist above. A clean <a href="/services/website-development/">hand-built business site</a> starts fast instead of being optimised back to fast.</p>
<h2>FAQs</h2>
<p><strong>Does speed directly affect Google rankings?</strong><br>Page experience signals (including Core Web Vitals) are ranking inputs, but the bigger effect is conversion: slow pages lose visitors before rankings even matter. Fix speed for revenue first, rankings second.</p>
<p><strong>What should I ask a developer about speed?</strong><br>Ask for before/after PageSpeed numbers on mobile, what they changed per layer above, and how they prevent regression (budgets, image rules). If the answer is "we installed a caching plugin," keep interviewing. Or skip the quiz — <a href="/consultation/book/">our free audit</a> includes a speed and <a href="/services/seo-optimization/">technical SEO</a> pass over your current site.</p>""",
},
"keyword-intent-mapping-the-secret-to-high-conversion-seo-campaigns": {
"meta_title": "Search Intent Mapping for SEO That Converts",
"meta_description": "Map keywords to intent: informational, commercial, transactional. One page per intent, right CTA each — with a small-business example.",
"tags": "SEO, Keyword Research, Search Intent",
"content": """<p><strong>Quick answer:</strong> keyword intent mapping means sorting every keyword you target into what the searcher actually wants — to learn, to compare, or to buy — and giving each intent its own page with a matching call to action. Most traffic-that-doesn't-convert problems are intent mismatches: a buyer landing on a learner's guide with no way to enquire, or a learner hit with pricing before they understand the service.</p>
<h2>The four intents, with business examples</h2>
<ul><li><strong>Informational</strong> ("how much does a website cost in Delhi") — wants an answer. Serve a thorough guide; CTA is a soft next step (related guide, free audit).</li><li><strong>Commercial investigation</strong> ("best website developer for restaurants") — comparing options. Serve comparisons, process, portfolio proof; CTA is a consultation.</li><li><strong>Transactional</strong> ("hire website developer Delhi", "book appointment") — ready to act. Serve a focused service/location page with the enquiry mechanism front and centre.</li><li><strong>Navigational</strong> ("GrowthSpare contact") — wants a specific page. Just make it findable; don't overthink it.</li></ul>
<h2>The mapping table to build</h2>
<p>List your keywords, label each with intent, then assign exactly one page per intent-cluster and one primary CTA per page. Two pages chasing the same intent cannibalise each other — Google splits the signal and neither ranks well. A Delhi clinic, for instance, wants separate pages for "dental implant cost" (informational guide), "best dentist near me" (location/authority page), and "book dental appointment" (booking page with WhatsApp CTA) — not one page trying to do all three, like our <a href="/industries/clinic-website-development/">clinic website structure</a> demonstrates.</p>
<h2>Auditing pages you already have</h2>
<p>Pull Search Console queries per page and ask: does the ranking query's intent match what this page does? A service page ranking for "how to" queries needs an educational section or a companion guide; a guide ranking for "hire/buy" queries needs a visible enquiry path added. Fix the mismatch before writing new content — it is the cheapest SEO win available.</p>
<h2>Measuring intent fit (not just rankings)</h2>
<p>Track queries (are commercial pages earning commercial queries?), click-through by intent (transactional titles should promise the action), and assisted conversions — an informational guide that feeds audit requests is converting even without a sale. Rankings without the right intent behind them are decoration.</p>
<h2>FAQs</h2>
<p><strong>How many keywords per page?</strong><br>One primary intent-cluster (a handful of close variants), not a count. Ten variants of "website developer Delhi" belong together; "website cost" belongs on its own guide.</p>
<p><strong>Can one page serve two intents?</strong><br>Sometimes — a location page can inform and convert — but designate a primary and design the CTA for it. If both intents are strong, two pages beat one compromised page. Our <a href="/services/seo-optimization/">SEO service</a> starts with exactly this mapping; <a href="/consultation/book/">ask for a free audit</a> and we'll show where your current pages mismatch.</p>""",
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
