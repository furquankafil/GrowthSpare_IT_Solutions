# Generated manually for Django 6.0.6
"""
Data migration completing the service landing pages for SEO + lead-gen purposes.

What this does (idempotent — safe to re-run):
1. Fills in `meta_title`, `meta_description`, `use_cases`, and `why_choose_us`
   for the 5 existing services, which were added as fields in migration 0003
   but never populated (the columns existed, empty, on every service).
2. Adds the 2 core services referenced in the company's service list but
   missing from this database — "Cyber Security Solutions" and
   "Custom Software Engineering" — using get_or_create so this never
   duplicates a service if it already exists (e.g. was added manually
   in the admin before this migration ran).
3. Adds 5 FAQs per service (35 total) — there were previously zero
   ServiceFAQ rows in the whole table. Each FAQ is only created if a
   FAQ with that exact question doesn't already exist for that service,
   so re-running this migration is safe.

No pricing figures were invented for the 2 new services — genuine
per-project pricing isn't available for MVP-scale reasoning here, so
they use "Contact for a Custom Quote" instead of a fabricated number,
consistent with how bespoke/variable-scope services are usually priced.
"""

from django.db import migrations


SERVICE_CONTENT = {
    "website-development": {
        "meta_title": "Business Website Development Services | GrowthSpare IT Solutions",
        "meta_description": "Custom, responsive business websites built for speed, SEO, and conversions. Get a fast-loading site that turns visitors into customers.",
        "use_cases": [
            "Small businesses that need a professional online presence",
            "Service businesses wanting an enquiry/contact-form driven site",
            "Companies replacing an outdated or slow existing website",
            "Startups launching a new product or business online for the first time",
        ],
        "why_choose_us": [
            "Websites built on clean, maintainable code — not locked-in page builders",
            "Performance and SEO considered from the first wireframe, not bolted on later",
            "Direct access to the team building your site, not a support ticket queue",
            "WhatsApp and contact-form lead capture built in from day one",
        ],
    },
    "digital-marketing": {
        "meta_title": "Digital Marketing Services for Small Businesses | GrowthSpare IT Solutions",
        "meta_description": "Cross-channel digital marketing — social media, lead generation, and Google Business Profile management — built around measurable pipeline results.",
        "use_cases": [
            "Local businesses wanting more calls and enquiries from nearby customers",
            "Companies launching a new product that needs an audience",
            "Businesses with a website but little to no incoming traffic",
            "Brands wanting a consistent presence across Google and social platforms",
        ],
        "why_choose_us": [
            "Campaigns tied to leads and enquiries, not just impressions",
            "Transparent monthly reporting so you always know what's working",
            "Marketing and web/tech built by the same team, so tracking is set up correctly",
            "No long lock-in contracts — month-to-month engagement",
        ],
    },
    "seo-optimization": {
        "meta_title": "SEO Services India | Rank Higher on Google | GrowthSpare IT Solutions",
        "meta_description": "Technical, on-page, and local SEO services to help your business rank higher on Google and grow organic traffic sustainably.",
        "use_cases": [
            "Businesses invisible on Google for their own service + city searches",
            "Websites with traffic that isn't converting into enquiries",
            "Local businesses wanting to rank for 'near me' and city-specific searches",
            "Sites that have been penalized or have technical SEO issues",
        ],
        "why_choose_us": [
            "SEO and web development under one roof, so technical fixes ship fast",
            "No keyword stuffing or shortcut tactics that risk future penalties",
            "Monthly reporting in plain language, not just raw analytics exports",
            "Focus on keywords that bring buying-intent traffic, not just volume",
        ],
    },
    "ai-whatsapp-automation": {
        "meta_title": "AI & WhatsApp Automation Services | GrowthSpare IT Solutions",
        "meta_description": "AI chatbots and WhatsApp automation for lead collection, appointment booking, and customer support — built on the WhatsApp Cloud API and OpenAI.",
        "use_cases": [
            "Businesses drowning in repetitive WhatsApp/DM enquiries",
            "Clinics, salons, and service businesses needing automated appointment booking",
            "E-commerce brands wanting instant WhatsApp order/FAQ replies",
            "Teams wanting to qualify leads automatically before a human follows up",
        ],
        "why_choose_us": [
            "Built on the official WhatsApp Cloud API, not unofficial/unstable wrappers",
            "Automations tailored to your actual sales process, not generic templates",
            "Human handoff built in — the bot escalates when it should",
            "Same team owns your website and CRM, so automations connect cleanly to your data",
        ],
    },
    "crm-software-development": {
        "meta_title": "Custom CRM Software Development | GrowthSpare IT Solutions",
        "meta_description": "Custom CRM systems for leads, customers, invoicing, and team permissions — built around your business instead of forcing you into generic SaaS.",
        "use_cases": [
            "Businesses outgrowing spreadsheets for tracking leads and customers",
            "Teams paying for multiple SaaS tools that don't quite fit their process",
            "Companies needing role-based access for sales, support, and admin staff",
            "Businesses wanting to own their customer data instead of renting access to it",
        ],
        "why_choose_us": [
            "One-time build, no per-seat SaaS subscription fees",
            "CRM shaped around your actual sales pipeline, not a generic template",
            "You own the codebase and the data outright",
            "Ongoing support from the team that actually built your system",
        ],
    },
}

NEW_SERVICES = [
    {
        "title": "Cyber Security Solutions",
        "slug": "cyber-security-solutions",
        "icon_class": "fas fa-shield-halved",
        "overview": "Security audits, hardening, and monitoring to protect your website and business systems from common threats.",
        "detailed_description": (
            "<p>A website or web app that isn't hardened is a liability, not an asset. We audit your existing "
            "infrastructure, fix common vulnerabilities, and put monitoring and best-practice security headers "
            "in place so your business systems stay protected.</p>"
        ),
        "features": "Security Audits\nVulnerability Scanning\nSecurity Headers & CSP Hardening\nRate Limiting & Abuse Protection\nSSL/TLS Configuration Review\nBackup & Recovery Planning",
        "benefits": "Reduced exposure to common attack vectors (XSS, CSRF, SQL injection)\nClear, prioritized report of what to fix and why\nSecurity built into your stack, not a one-time checkbox",
        "process_steps": "Infrastructure & Codebase Security Audit\nVulnerability Identification & Risk Prioritization\nHardening Implementation (headers, rate limits, validation)\nMonitoring & Documentation Handover",
        "technologies": "Django Security Middleware, django-ratelimit, OWASP guidelines, SSL/TLS, CSP",
        "pricing_estimate": "Contact for a Custom Quote",
        "meta_title": "Cyber Security Services for Websites & Web Apps | GrowthSpare IT Solutions",
        "meta_description": "Security audits, hardening, and monitoring for business websites and web applications. Identify and fix vulnerabilities before they become incidents.",
        "use_cases": [
            "Businesses that have never had their website security-audited",
            "Companies handling customer data (forms, accounts, payments) online",
            "Sites recovering from a previous security incident or spam attack",
            "Teams preparing for a compliance or client security review",
        ],
        "why_choose_us": [
            "Practical, prioritized fixes — not a jargon-heavy report you can't act on",
            "Security work done by the same engineers who understand your existing codebase",
            "No fear-based upselling — clear explanation of actual risk levels",
            "Ongoing monitoring available after the initial audit",
        ],
        "cta_headline": "Find out how exposed your website really is.",
        "cta_subtext": "Get a security audit and a clear, prioritized list of what to fix first.",
    },
    {
        "title": "Custom Software Engineering",
        "slug": "custom-software-engineering",
        "icon_class": "fas fa-code",
        "overview": "Bespoke software built around your exact workflow — internal tools, dashboards, integrations, and systems that off-the-shelf software can't handle.",
        "detailed_description": (
            "<p>When your business process doesn't fit neatly into off-the-shelf software, we build the tool that "
            "does. From internal dashboards to third-party API integrations, we design and ship software specific "
            "to how your business actually operates.</p>"
        ),
        "features": "Custom Internal Tools\nThird-Party API Integrations\nWorkflow Automation\nAdmin Dashboards\nData Migration & Reporting Tools\nCloud Deployment & Maintenance",
        "benefits": "Software that matches your workflow instead of forcing you to adapt to it\nNo recurring per-seat licensing for tools you'd otherwise rent\nDirect ownership of the codebase and your data",
        "process_steps": "Requirement & Workflow Discovery\nSystem Architecture & Scoping\nIterative Development with Regular Check-ins\nDeployment, Testing & Handover",
        "technologies": "Python, Django, PostgreSQL, REST APIs, Docker",
        "pricing_estimate": "Contact for a Custom Quote",
        "meta_title": "Custom Software Development Services | GrowthSpare IT Solutions",
        "meta_description": "Bespoke software, internal tools, and system integrations built around your exact business workflow — for needs off-the-shelf software can't cover.",
        "use_cases": [
            "Businesses with a manual process that's outgrown spreadsheets or email",
            "Companies needing two or more existing tools connected together",
            "Teams needing an internal dashboard for operations, inventory, or reporting",
            "Businesses with a workflow no off-the-shelf SaaS product quite fits",
        ],
        "why_choose_us": [
            "Software scoped around your actual process, not a generic template",
            "Transparent, iterative development with regular check-ins — no year-long black box",
            "You own the code and can take it anywhere afterward",
            "Same team available for support and iteration after launch",
        ],
        "cta_headline": "Describe your workflow — we'll tell you if custom software makes sense.",
        "cta_subtext": "Book a free scoping call before committing to anything.",
    },
]

# 5 FAQs per service. Written per-service so answers are specific rather than
# generic filler repeated across every page (which would hurt, not help, SEO).
SERVICE_FAQS = {
    "website-development": [
        ("How long does it take to build a business website?", "Most standard business websites are delivered in 2-4 weeks depending on the number of pages and content readiness. We'll give you an exact timeline after understanding your requirements."),
        ("Will my website work well on mobile phones?", "Yes. Every website we build is fully responsive and tested across mobile, tablet, and desktop viewports before launch."),
        ("Do you provide website maintenance after launch?", "Yes, we offer ongoing maintenance and support plans so your site stays updated, secure, and running smoothly."),
        ("Can you integrate WhatsApp and contact forms into my site?", "Yes, WhatsApp click-to-chat and validated contact forms are included as standard on every business website we build."),
        ("Do you work with businesses outside Delhi?", "Yes, we work with clients across India and internationally — all communication and project delivery happens remotely."),
    ],
    "digital-marketing": [
        ("How much does digital marketing cost for a small business?", "It depends on the channels and scope involved. Get in touch with your goals and budget and we'll recommend a realistic starting plan."),
        ("How soon will I see results from digital marketing?", "Some channels like social media and Google Business Profile can show early engagement within weeks, while SEO-driven organic growth typically takes longer. We'll set honest expectations upfront."),
        ("Do you manage my social media accounts directly?", "Yes, we can manage content planning, posting, and reporting for your business's social media profiles."),
        ("Can you help with Google Business Profile optimization?", "Yes, Google Business Profile setup and optimization is part of our digital marketing service for local businesses."),
        ("Will I get performance reports?", "Yes, you'll receive regular performance reports showing what's working and where budget is going."),
    ],
    "seo-optimization": [
        ("How much does SEO cost?", "SEO pricing depends on your website's current state and competitiveness of your target keywords. Contact us for a quote based on your specific site."),
        ("How long does SEO take to show results?", "SEO is a compounding channel — most businesses start seeing meaningful movement in 3-6 months, with continued growth after that."),
        ("Do you guarantee first-page Google rankings?", "No legitimate SEO service can guarantee specific rankings — Google's algorithm isn't controlled by any agency. We focus on sustainable, white-hat practices that build lasting organic visibility."),
        ("Is local SEO different from regular SEO?", "Yes, local SEO focuses on ranking for location-based searches (like 'near me' queries) and Google Business Profile visibility, alongside standard on-page and technical SEO."),
        ("Do you provide monthly SEO reports?", "Yes, you'll get monthly reports covering rankings, organic traffic trends, and completed optimization work."),
    ],
    "ai-whatsapp-automation": [
        ("Do you use the official WhatsApp Business API?", "Yes, our automations are built on the official WhatsApp Cloud API, not unofficial tools that risk your number getting banned."),
        ("Can the AI chatbot hand off to a human?", "Yes, every automation we build includes a clear handoff path so complex queries reach a real team member."),
        ("Can WhatsApp automation handle appointment bookings?", "Yes, we build booking flows directly into WhatsApp so customers can schedule appointments without leaving the chat."),
        ("What AI model powers the chatbots?", "We typically build on OpenAI's models, configured and trained around your specific business context and FAQs."),
        ("Is this only for e-commerce businesses?", "No — clinics, salons, real estate, service businesses, and B2B companies all use WhatsApp automation for lead capture and support."),
    ],
    "crm-software-development": [
        ("Why build a custom CRM instead of using Salesforce or Zoho?", "Off-the-shelf CRMs charge per-seat monthly fees and often don't match your exact sales process. A custom CRM is a one-time build, tailored to your workflow, that you fully own."),
        ("How long does it take to build a custom CRM?", "Timelines vary by scope, but most CRM projects take 6-10 weeks from requirement finalization to launch."),
        ("Can the CRM handle role-based permissions for my team?", "Yes, role-based access control for sales, support, and admin staff is a core part of every CRM we build."),
        ("Will I own the CRM's source code?", "Yes, you fully own the codebase and your data — there's no vendor lock-in."),
        ("Can you migrate our existing data into the new CRM?", "Yes, data migration from spreadsheets or an existing system is something we plan for as part of the project scope."),
    ],
    "cyber-security-solutions": [
        ("What does a security audit actually cover?", "We review your website/app's infrastructure, code, headers, and configuration for common vulnerabilities like XSS, CSRF, SQL injection, and insecure settings, then deliver a prioritized report."),
        ("My site was hacked or spammed before — can you help?", "Yes, we can investigate the likely cause, clean up affected areas, and harden your systems to reduce the chance of it happening again."),
        ("Do I need a security audit if my site is small?", "Smaller sites are targeted by automated bots just as often as large ones, especially if they collect customer data through forms or accounts."),
        ("Do you offer ongoing security monitoring, not just a one-time audit?", "Yes, ongoing monitoring is available as a follow-on service after the initial audit."),
        ("Will fixing security issues slow down my website?", "No — proper security hardening (like rate limiting and header configuration) has negligible performance impact when implemented correctly."),
    ],
    "custom-software-engineering": [
        ("What kind of projects count as 'custom software'?", "Internal tools, admin dashboards, workflow automations, and integrations between existing systems (e.g. your website and accounting software) are all common examples."),
        ("How is this different from your CRM development service?", "CRM development is one specific type of custom software focused on managing leads and customers. Custom software engineering covers a broader range of business tools beyond CRM."),
        ("Do you provide ongoing support after the software is delivered?", "Yes, we offer maintenance and support plans, and remain available for future iterations as your needs change."),
        ("Can you integrate with tools we already use?", "Yes, integrating with existing third-party APIs and tools is a common part of custom software projects."),
        ("How do you scope a custom software project before starting?", "We start with a discovery call to understand your workflow, followed by a scoping document outlining what will be built, the timeline, and cost, before any development begins."),
    ],
}


def populate_service_content(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    ServiceCategory = apps.get_model("services", "ServiceCategory")
    ServiceFAQ = apps.get_model("services", "ServiceFAQ")

    # --- 1. Backfill missing content on existing services ---
    for slug, content in SERVICE_CONTENT.items():
        try:
            service = Service.objects.get(slug=slug)
        except Service.DoesNotExist:
            continue

        service.meta_title = content["meta_title"]
        service.meta_description = content["meta_description"]
        service.use_cases = "\n".join(content["use_cases"])
        service.why_choose_us = "\n".join(content["why_choose_us"])
        service.save()

    # --- 2. Add the 2 missing core services, mapped into the existing
    #        "Web Solutions" category (no new ServiceCategory rows added,
    #        since the model intentionally restricts to 5 verified
    #        categories) ---
    web_solutions_category = ServiceCategory.objects.filter(slug="web-solutions").first()

    for entry in NEW_SERVICES:
        use_cases = entry.pop("use_cases")
        why_choose_us = entry.pop("why_choose_us")
        slug = entry["slug"]

        service, created = Service.objects.get_or_create(
            slug=slug,
            defaults={
                **entry,
                "use_cases": "\n".join(use_cases),
                "why_choose_us": "\n".join(why_choose_us),
                "is_active": True,
            },
        )
        if created and web_solutions_category:
            service.categories.add(web_solutions_category)

    # --- 3. Add FAQs (idempotent per service+question) ---
    for slug, faqs in SERVICE_FAQS.items():
        try:
            service = Service.objects.get(slug=slug)
        except Service.DoesNotExist:
            continue

        existing_questions = set(
            service.service_faqs.values_list("question", flat=True)
        )
        for order, (question, answer) in enumerate(faqs):
            if question in existing_questions:
                continue
            ServiceFAQ.objects.create(
                service=service,
                question=question,
                answer=answer,
                order=order,
            )


def noop_reverse(apps, schema_editor):
    """Content-only migration — nothing structural to reverse."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0003_service_use_cases_why_choose_cta'),
    ]

    operations = [
        migrations.RunPython(populate_service_content, noop_reverse),
    ]
