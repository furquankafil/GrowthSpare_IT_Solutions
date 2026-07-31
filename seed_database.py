"""
GrowthSpare IT Solutions - 7-Division Database Seeding Suite.
Populates the database with our 7 core services (each with premium,
consulting-grade content: overview, features, benefits, use cases, why-choose-us,
and CTA copy), 29 realistic demo projects, 18 blog insights, 40 FAQ items,
and testimonials, aligned under our 7 active business divisions:
1. Web Solutions
2. AI Automation
3. SaaS & CRM Systems
4. Digital Marketing
5. SEO & Marketing
6. Cyber Security
7. Engineering Solutions

Usage:
- Run 'python seed_database.py' in your PowerShell terminal.
"""

import os

import django

# Initialize the Django Environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

from django.conf import settings  # noqa: E402  (must follow django.setup())
from django.db import transaction  # noqa: E402

# Import all models safely
from apps.accounts.models import User
from apps.services.models import Service, ServiceCategory, ServiceFAQ
from apps.portfolio.models import Project, ProjectCategory, ProjectImage
from apps.blog.models import BlogPost, BlogCategory, BlogComment
from apps.faq.models import FAQCategory, FAQItem
from apps.testimonials.models import Testimonial
from apps.dashboard.models import SystemAnnouncement
from apps.core.models import ClientLogo


@transaction.atomic
def seed_all_data():
    print("GrowthSpare IT Solutions dynamic 7-Division database seeding started...")

    # ==============================================================================
    # A. OPTIONAL DESTRUCTIVE CLEANUP (opt-in only, never runs by accident)
    # ==============================================================================
    # Wiping is destructive and must be explicitly requested via the
    # SEED_RESET_DB environment variable, and is further restricted to
    # DEBUG environments so it can never accidentally run in production.
    # By default the seeder runs in pure upsert mode (see update_or_create /
    # get_or_create calls below), so re-running this script is safe and
    # will not duplicate or wipe existing data.
    reset_requested = os.environ.get("SEED_RESET_DB", "false").lower() == "true"
    if reset_requested:
        if not settings.DEBUG:
            raise RuntimeError(
                "SEED_RESET_DB=true was requested but DEBUG is disabled. "
                "Refusing to wipe a non-development database."
            )
        print("-> SEED_RESET_DB=true: performing destructive cleanup of old records...")
        SystemAnnouncement.objects.all().delete()
        ClientLogo.objects.all().delete()
        Testimonial.objects.all().delete()
        FAQItem.objects.all().delete()
        FAQCategory.objects.all().delete()
        BlogComment.objects.all().delete()
        BlogPost.objects.all().delete()
        BlogCategory.objects.all().delete()
        ProjectImage.objects.all().delete()
        Project.objects.all().delete()
        ProjectCategory.objects.all().delete()
        ServiceFAQ.objects.all().delete()
        Service.objects.all().delete()
        ServiceCategory.objects.all().delete()
    else:
        print("-> Skipping destructive cleanup (upsert mode). Set SEED_RESET_DB=true in a DEBUG "
              "environment to wipe seed-managed tables first.")

    # ==============================================================================
    # B. CREATING ADMINISTRATOR/AUTHOR
    # ==============================================================================
    author = User.objects.filter(is_staff=True).first()
    if not author:
        admin_username = os.environ.get("SEED_ADMIN_USERNAME")
        admin_email = os.environ.get("SEED_ADMIN_EMAIL")
        admin_password = os.environ.get("SEED_ADMIN_PASSWORD")
        if not all([admin_username, admin_email, admin_password]):
            raise RuntimeError(
                "No administrator account exists yet. Set SEED_ADMIN_USERNAME, "
                "SEED_ADMIN_EMAIL and SEED_ADMIN_PASSWORD environment variables "
                "before running the seeder so a default administrator can be created."
            )
        print("-> Creating default administrator account...")
        author = User.objects.create_superuser(
            username=admin_username,
            email=admin_email,
            password=admin_password,
            first_name=os.environ.get("SEED_ADMIN_FIRST_NAME", "Admin"),
            last_name=os.environ.get("SEED_ADMIN_LAST_NAME", "User"),
            role="ADMIN",
            is_email_verified=True
        )
    else:
        print("-> Using existing administrator account.")

    # ==============================================================================
    # C. SEED SERVICE CATEGORIES & 7 CORE SERVICES (With Many-to-Many mappings)
    # ==============================================================================
    print("-> Seeding Service Categories...")

    def _get_or_create_service_category(name, slug, order):
        obj, _ = ServiceCategory.objects.update_or_create(
            slug=slug, defaults={"name": name, "order": order}
        )
        return obj

    sc_web = _get_or_create_service_category("Web Solutions", "web-solutions", 1)
    sc_ai = _get_or_create_service_category("AI Automation", "ai-automation", 2)
    sc_crm = _get_or_create_service_category("SaaS & CRM Systems", "saas-crm-systems", 3)
    sc_digital = _get_or_create_service_category("Digital Marketing", "digital-marketing", 4)
    sc_seo = _get_or_create_service_category("SEO & Marketing", "seo-marketing", 5)
    sc_cyber = _get_or_create_service_category("Cyber Security", "cyber-security", 6)
    sc_eng = _get_or_create_service_category("Engineering Solutions", "engineering-solutions", 7)

    print("-> Seeding 7 Core Services (premium consulting-grade content)...")
    services_data = [
        {
            "title": "Website Development",
            "icon_class": "fas fa-desktop",
            "overview": "Enterprise-grade, conversion-focused websites engineered to represent your brand and turn visitors into paying customers.",
            "detailed_description": (
                "<p>Your website is your digital corporate office — often the very first impression a prospect forms of your business. "
                "GrowthSpare designs and engineers responsive, accessible, and lightning-fast websites that look exceptional on every "
                "device and are technically optimized to score above 95 on Google Lighthouse audits.</p>"
                "<p>From single-page brand showcases to multi-module business platforms, every build is hand-coded with semantic HTML, "
                "modern CSS architecture, and a Django backend that gives you full ownership of your content — no rented page builders, "
                "no recurring subscription lock-in.</p>"
            ),
            "features": (
                "Fully Responsive, Mobile-First Design\nSEO-Friendly Semantic Markup\nSub-2-Second Page Load Speeds\n"
                "Custom Contact & Lead-Capture Forms\nGoogle Maps & Location Integration\nWhatsApp Chat Integration\n"
                "Secure Admin Dashboard for Content Updates\nSSL, Backups & Ongoing Technical Support"
            ),
            "benefits": (
                "Lighthouse performance scores consistently above 95%\nFully responsive across every mobile, tablet and desktop viewport\n"
                "Full compliance with WCAG accessibility standards\nStronger organic search visibility from day one\n"
                "Complete ownership of your codebase — no third-party platform lock-in"
            ),
            "process_steps": (
                "Discovery Call & Requirement Mapping\nFigma Wireframe & Brand Design Validation\n"
                "Semantic Front-End Assembly\nDjango Backend & CMS Integration\nQA Testing & Brotli Asset Compression\n"
                "Launch, Monitoring & Handover Training"
            ),
            "technologies": "HTML5, CSS3, JavaScript, Tailwind CSS, Bootstrap, Python, Django, PostgreSQL",
            "use_cases": (
                "Corporate & brand showcase websites for SMEs and startups\nRestaurant, clinic and salon booking websites\n"
                "Real estate and property listing portals\nEducational institution and LMS websites\n"
                "Event ticketing and hospitality booking platforms\nNGO, portfolio and personal brand websites"
            ),
            "why_choose_us": (
                "Hand-engineered code — not templated page builders\nDedicated project manager from kickoff to launch\n"
                "Transparent, milestone-based delivery timelines\nPost-launch support and priority bug-fix SLA\n"
                "Performance and accessibility audited before every handover"
            ),
            "cta_headline": "Ready for a website that actually converts?",
            "cta_subtext": "Let's scope your project and map out a realistic launch timeline together.",
            "pricing_estimate": "Starting at ₹4,999",
            "cat_obj": sc_web
        },
        {
            "title": "Digital Marketing & Growth",
            "icon_class": "fas fa-chart-line",
            "overview": "Full-funnel digital growth strategies engineered to acquire high-value customers and compound revenue predictably.",
            "detailed_description": (
                "<p>GrowthSpare builds high-ROI digital growth funnels that go beyond vanity metrics. We manage data-driven, cross-channel "
                "campaigns across social, search and marketplace touchpoints, designed to acquire high-intent enterprise and consumer "
                "leads at a sustainable cost.</p>"
                "<p>Every campaign is instrumented with proper analytics and attribution from day one, so you always know exactly which "
                "channel, creative, and audience segment is driving real business outcomes — not just clicks.</p>"
            ),
            "features": (
                "Social Media Marketing & Content Calendars\nPaid Lead Generation Campaigns\nBrand Awareness & Positioning Strategy\n"
                "Google Business Profile Optimization\nMonthly Performance & ROI Reports\nMarketing Automation Workflows\n"
                "Conversion Rate Optimization (CRO)"
            ),
            "benefits": (
                "Drastic reduction in customer acquisition cost\nMaximized ad-spend efficiency across channels\n"
                "Transparent pipeline ROI metrics on every campaign\nCompounding brand authority over time\n"
                "Clear monthly reporting your leadership team can act on"
            ),
            "process_steps": (
                "Funnel & Analytics Audit\nTarget Audience & Persona Profiling\nCampaign Creative Development & Launch\n"
                "Continuous Conversion Tuning\nMonthly Strategy Review"
            ),
            "technologies": "Google Analytics 4, Meta Ads Manager, Meta Pixel, Google Tag Manager, Hotjar, Canva, Zapier",
            "use_cases": (
                "D2C and e-commerce brands scaling paid acquisition\nB2B companies building LinkedIn lead pipelines\n"
                "Local businesses growing foot traffic via Google Business Profile\n"
                "Product launches needing a coordinated cross-channel push\nSubscription businesses reducing churn through retargeting"
            ),
            "why_choose_us": (
                "Data-first approach — every rupee of spend is tracked\nCross-channel strategy instead of single-platform tunnel vision\n"
                "Dedicated growth manager, not a rotating agency account team\nMonthly reporting in plain business language, not jargon\n"
                "Flexible retainers that scale with your growth stage"
            ),
            "cta_headline": "Ready to turn marketing spend into predictable growth?",
            "cta_subtext": "Book a free growth audit and see where your funnel is leaking revenue.",
            "pricing_estimate": "Starting at ₹5,999/month",
            "cat_obj": sc_digital
        },
        {
            "title": "SEO Optimization",
            "icon_class": "fas fa-magnifying-glass-chart",
            "overview": "Sustainable, white-hat search engine optimization that compounds your organic visibility and reduces reliance on paid ads.",
            "detailed_description": (
                "<p>Visibility on Google translates directly into revenue. GrowthSpare optimizes on-page semantic HTML, integrates JSON-LD "
                "structured data schemas, and configures Search Console monitoring tunnels to grow your organic traffic safely and "
                "sustainably — no black-hat shortcuts that risk future penalties.</p>"
                "<p>Our approach blends technical SEO health, content strategy, and authoritative link building so that your rankings keep "
                "compounding long after the initial engagement.</p>"
            ),
            "features": (
                "On-Page SEO Optimization\nTechnical SEO Audits & Fixes\nLocal SEO & Google Maps Ranking\n"
                "Keyword Research & Competitive Mapping\nContent Strategy & Optimization\nMonthly Ranking & Traffic Reports\n"
                "Structured Data (Schema.org) Implementation"
            ),
            "benefits": (
                "2x increase in organic click-through metrics on average\nStable, compounding organic search channel traffic\n"
                "Top search results captured for high-intent keywords\nReduced long-term dependency on paid advertising\n"
                "Fully transparent, real-time ranking dashboards"
            ),
            "process_steps": (
                "Technical SEO Crawl Audit\nCompetitive Keyword Mapping\nSemantic Content Optimization\n"
                "Schema Rich Snippet Ingestion\nAuthority Building & Monthly Monitoring"
            ),
            "technologies": "Google Search Console, Google Analytics 4, Schema.org, Ahrefs, Screaming Frog",
            "use_cases": (
                "Local service businesses competing for map-pack rankings\nE-commerce stores optimizing category and product pages\n"
                "SaaS companies building organic content pipelines\nMulti-location brands needing local SEO at scale\n"
                "Legacy websites recovering from a ranking drop or penalty"
            ),
            "why_choose_us": (
                "100% white-hat, Google-guideline compliant methodology\nTechnical depth beyond generic keyword-stuffing tactics\n"
                "Real-time, transparent Search Console reporting access\nContent and technical SEO handled under one roof\n"
                "Long-term partnership focus over one-off audits"
            ),
            "cta_headline": "Ready to own page one of Google?",
            "cta_subtext": "Get a free technical SEO audit and a clear roadmap to higher rankings.",
            "pricing_estimate": "Starting at ₹3,999/month",
            "cat_obj": sc_seo
        },
        {
            "title": "AI & WhatsApp Automation",
            "icon_class": "fas fa-robot",
            "overview": "Automate customer support, appointment booking, FAQs, and lead collection using AI-powered chatbots and WhatsApp automation.",
            "detailed_description": (
                "<p>GrowthSpare designs event-driven WhatsApp webhook receivers that automatically process incoming messages, "
                "pre-qualify customer requirements, and update contact records seamlessly using large language model workflows.</p>"
                "<p>The result is a 24/7 digital front desk for your business — one that never sleeps, never misses a lead, and hands "
                "off to a human teammate the moment a conversation needs a personal touch.</p>"
            ),
            "features": (
                "Custom AI Chatbots (Website & WhatsApp)\nWhatsApp Business API Automation\n"
                "Automated Lead Collection & Qualification\nAppointment Booking & Reminders\n"
                "24/7 Automated Customer Support\nCRM & Calendar Integrations\nConversation Analytics Dashboard"
            ),
            "benefits": (
                "Reduce manual operational workload by up to 70%\nEliminate response-time gaps outside business hours\n"
                "Scale customer conversations 24/7 without added headcount\nCapture and qualify every inbound lead automatically\n"
                "Consistent, on-brand responses across every conversation"
            ),
            "process_steps": (
                "Technical API Scoping & Requirement Analysis\nWorkflow Logic Blueprinting\n"
                "Custom Webhook & LLM Prompt Engineering\nSandboxed Testing & Integrity Deployment\nLive Monitoring & Continuous Tuning"
            ),
            "technologies": "Python, Django, WhatsApp Cloud API, OpenAI GPT-4o, Celery, Redis, Twilio",
            "use_cases": (
                "Clinics and salons automating appointment booking\nReal estate teams pre-qualifying property inquiries\n"
                "E-commerce brands automating order status updates\nEducational institutes automating admissions FAQs\n"
                "Service businesses capturing after-hours leads automatically"
            ),
            "why_choose_us": (
                "Deep hands-on experience with the WhatsApp Cloud API\nCustom LLM workflows tailored to your exact business logic\n"
                "Human hand-off built in — automation without losing the personal touch\nSecure, containerized deployments with monitored uptime\n"
                "Ongoing tuning as your conversation volume grows"
            ),
            "cta_headline": "Ready to put your customer support on autopilot?",
            "cta_subtext": "Talk to us about the workflows costing your team the most manual hours.",
            "pricing_estimate": "Starting at ₹7,999",
            "cat_obj": sc_ai
        },
        {
            "title": "CRM Software Development",
            "icon_class": "fas fa-users-gear",
            "overview": "Custom CRM systems to manage leads, customers, invoices, employees, and business operations — built around how you actually work.",
            "detailed_description": (
                "<p>Bypass generic third-party SaaS fees and rigid workflows. GrowthSpare builds custom, private CRM platforms designed "
                "around your specific sales pipeline, team permission structure, and invoicing parameters.</p>"
                "<p>Because you own the codebase and the database, there's no per-seat pricing creep, no vendor lock-in, and no compromise "
                "between what the software does and what your business actually needs.</p>"
            ),
            "features": (
                "Lead & Pipeline Management\nSales & Revenue Dashboards\nCustomer & Contact Database\n"
                "Custom Reports & Analytics\nRole-Based Access Management\nInvoicing & Billing Modules\n"
                "Cloud Deployment & Automated Backups"
            ),
            "benefits": (
                "Save thousands in recurring monthly SaaS seat costs\nOwn your entire customer and sales database outright\n"
                "Tailored precisely to your existing business workflow\nNo artificial feature or user-seat limits\nScales cleanly as your team grows"
            ),
            "process_steps": (
                "Lead Pipeline & Workflow Mapping\nDatabase Schema Design & Normalization\n"
                "Dashboard & Interface Construction\nSecure Multi-Tenancy & Role Hardening\nTraining & Go-Live Support"
            ),
            "technologies": "Python, Django, PostgreSQL, Chart.js, Bootstrap 5, Celery, Redis",
            "use_cases": (
                "Sales teams outgrowing spreadsheet-based tracking\nAgencies managing multi-client pipelines and invoicing\n"
                "Manufacturing and distribution businesses tracking B2B accounts\n"
                "Service companies needing role-based team dashboards\nCompanies migrating away from expensive per-seat SaaS CRMs"
            ),
            "why_choose_us": (
                "Full source-code ownership — no vendor lock-in, ever\nBuilt around your actual sales process, not a generic template\n"
                "Transparent, one-time development cost vs. endless subscriptions\nSecure role-based permissions built in from day one\n"
                "Ongoing feature development available as your business evolves"
            ),
            "cta_headline": "Tired of paying per-seat for software you don't fully control?",
            "cta_subtext": "Let's map your sales process into a CRM you actually own.",
            "pricing_estimate": "Starting from ₹24,999",
            "cat_obj": sc_crm
        },
        {
            "title": "Cyber Security Solutions",
            "icon_class": "fas fa-shield-halved",
            "overview": "Enterprise-grade security audits, hardening, and monitoring that protect your business, customer data, and reputation.",
            "detailed_description": (
                "<p>A single breach can cost far more than the software it exploited — in downtime, regulatory exposure, and lost customer "
                "trust. GrowthSpare's cyber security division audits your applications, infrastructure, and access policies to close "
                "gaps before attackers find them.</p>"
                "<p>We work across the stack: web application hardening, server and network configuration review, secure authentication "
                "design, and ongoing vulnerability monitoring — all documented in plain-language reports your leadership team can act on.</p>"
            ),
            "features": (
                "Web Application Security Audits\nVulnerability Assessment & Penetration Testing\n"
                "Secure Authentication & Access Control Design\nServer & Network Hardening\nSSL/TLS & Data Encryption Setup\n"
                "Ongoing Security Monitoring & Alerts\nIncident Response Planning & Compliance Documentation"
            ),
            "benefits": (
                "Significantly reduced exposure to breaches and data leaks\nClear, prioritized remediation roadmap, not just a raw scan report\n"
                "Stronger customer and stakeholder trust in your platform\nImproved readiness for compliance and security questionnaires\n"
                "Faster detection and response when incidents do occur"
            ),
            "process_steps": (
                "Attack Surface & Asset Discovery\nVulnerability Assessment & Penetration Testing\n"
                "Prioritized Risk & Remediation Reporting\nHardening & Fix Implementation Support\n"
                "Ongoing Monitoring & Quarterly Re-Audits"
            ),
            "technologies": "OWASP ZAP, Nmap, Burp Suite, Let's Encrypt/TLS, Cloudflare, Fail2Ban, Django Security Middleware",
            "use_cases": (
                "SaaS platforms preparing for enterprise security reviews\nE-commerce sites handling customer payment data\n"
                "Businesses that recently experienced a security incident\nCompanies preparing for ISO 27001 or SOC 2 readiness\n"
                "Websites and APIs due for a periodic security health check"
            ),
            "why_choose_us": (
                "Findings delivered in plain business language, not just raw scan output\nPrioritized remediation roadmap, not an overwhelming vulnerability dump\n"
                "Hands-on hardening support, not just an audit-and-leave engagement\nOngoing monitoring options for continuous protection\n"
                "Same engineering team that can also implement the fixes"
            ),
            "cta_headline": "Ready to find out where your real security gaps are?",
            "cta_subtext": "Book a confidential security assessment before someone else finds the gap first.",
            "pricing_estimate": "Starting at ₹14,999",
            "cat_obj": sc_cyber
        },
        {
            "title": "Custom Software Engineering",
            "icon_class": "fas fa-gears",
            "overview": "Bespoke software engineering — from backend systems and APIs to internal tools and DevOps pipelines — built to enterprise engineering standards.",
            "detailed_description": (
                "<p>Some problems don't fit a template. GrowthSpare's engineering division designs and builds custom backend systems, "
                "REST APIs, internal tooling, and cloud infrastructure for businesses whose requirements go beyond off-the-shelf software.</p>"
                "<p>Every engagement follows disciplined engineering practices — version control, automated testing, containerized "
                "deployments, and clear technical documentation — so what we hand over is maintainable long after launch, whether by our "
                "team or yours.</p>"
            ),
            "features": (
                "Custom Backend & API Development\nSystem Architecture & Database Design\n"
                "Cloud Infrastructure & DevOps Pipelines\nThird-Party & Legacy System Integrations\n"
                "Internal Tools & Automation Scripts\nContainerization (Docker) & CI/CD Setup\nCode Audits & Technical Due Diligence"
            ),
            "benefits": (
                "Software architected specifically around your business logic\nReduced technical debt through disciplined engineering practices\n"
                "Improved system reliability, scalability, and uptime\nFaster future development thanks to clean documentation\n"
                "Independent technical due diligence for investment or acquisition readiness"
            ),
            "process_steps": (
                "Technical Discovery & Architecture Planning\nDatabase & System Design\n"
                "Iterative Engineering Sprints with Testing\nContainerized Deployment & CI/CD Setup\nDocumentation, Handover & Support"
            ),
            "technologies": "Python, Django, Django REST Framework, PostgreSQL, Docker, Redis, Celery, Nginx, Gunicorn, Git",
            "use_cases": (
                "Startups needing a custom backend beyond no-code tools\nCompanies integrating disparate legacy systems via APIs\n"
                "Businesses building internal dashboards and automation tools\nTeams needing DevOps pipelines and cloud migration support\n"
                "Founders needing technical due diligence before fundraising or acquisition"
            ),
            "why_choose_us": (
                "Enterprise-grade engineering discipline at SME-friendly pricing\nClean, documented, maintainable code — not disposable scripts\n"
                "Experience across backend, DevOps, and systems integration\nClear sprint-based delivery with visible progress at every stage\n"
                "Long-term technical partnership, not a one-off handoff"
            ),
            "cta_headline": "Have a technical challenge that doesn't fit a template?",
            "cta_subtext": "Let's talk through your architecture and scope an engineering plan.",
            "pricing_estimate": "Starting from ₹29,999",
            "cat_obj": sc_eng
        }
    ]

    for s_data in services_data:
        cat_obj = s_data.pop("cat_obj")
        title = s_data.pop("title")
        service, _ = Service.objects.update_or_create(title=title, defaults=s_data)
        service.categories.add(cat_obj)  # Map multiple categories using Many-to-Many dynamic methods [1]

    print(f"-> Successfully seeded {Service.objects.count()} core services.")

    # ==============================================================================
    # D. SEED DYNAMIC PORTFOLIO CATEGORIES & EXACT 29 REALISTIC DEMO PROJECTS
    # ==============================================================================
    print("-> Seeding Project Categories...")

    def _get_or_create_project_category(name, slug):
        obj, _ = ProjectCategory.objects.update_or_create(slug=slug, defaults={"name": name})
        return obj

    cat_web = _get_or_create_project_category("Website Development", "website-development")
    cat_ai = _get_or_create_project_category("AI Automation", "ai-automation")
    cat_saas = _get_or_create_project_category("CRM & SaaS Solutions", "crm-saas-solutions")
    cat_growth = _get_or_create_project_category("Digital Marketing", "digital-marketing")
    cat_seo = _get_or_create_project_category("SEO Optimization", "seo-optimization")
    cat_crm = cat_saas  # Alias to prevent NameError [1]

    print("-> Seeding exactly 29 Realistic Case Studies with high-res Unsplash photos...")
    
    # 29 realistic demo/concept projects with actual timelines (2-8 weeks)
    portfolio_projects_data = [
        # --- Website Development (4 projects) ---
        {
            "title": "BiteCraft - Restaurant Website for Spice Garden",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=800&q=80",
            "client_name": "Spice Garden",
            "industry": "Hospitality & Food Service",
            "problem_statement": "The restaurant lost online table reservations to third-party aggregators charging high commissions, and their PDF menu loaded slowly on mobile devices.",
            "solution_statement": "GrowthSpare developed a secure, responsive brand showcase website featuring an interactive menu, digital reservation tables, and clean Google Maps API locations.",
            "results_statement": "Completed in 3 weeks. Direct reservation leads rose by 35% in its first month, completely bypassing third-party fees.",
            "technology_stack": "HTML5, CSS3, Tailwind CSS, JavaScript, Django, PostgreSQL",
            "project_duration": "3 Weeks",
            "tags": "Restaurant, Booking, Menu, Django",
            "is_featured": True
        },
        {
            "title": "SmileCare - Professional Dental Clinic Website",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1629909613654-28e377c37b09?auto=format&fit=crop&w=800&q=80",
            "client_name": "SmileCare Dental",
            "industry": "Healthcare & Dentistry",
            "problem_statement": "The dental clinic faced operational overhead because patients booked appointments solely over manual phone calls, leading to scheduling friction.",
            "solution_statement": "We developed a clean, responsive clinic website featuring patient profiles, a dynamic appointment calendar, and automated SMS appointment verification alerts.",
            "results_statement": "Completed in 3 weeks. Reduced scheduling friction by 40% and improved patient appointment show-up rates by 25%.",
            "technology_stack": "HTML5, CSS3, Bootstrap 5, Django, SQLite, Twilio",
            "project_duration": "3 Weeks",
            "tags": "Healthcare, Appointment, SMS, Bootstrap",
            "is_featured": True
        },
        {
            "title": "IronPulse - Modern Gym & Fitness Website",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?auto=format&fit=crop&w=800&q=80",
            "client_name": "IronPulse Fitness",
            "industry": "Fitness & Health",
            "problem_statement": "IronPulse Gym required a high-converting, modern website to showcase class schedules, trainer profiles, and simplify membership plans.",
            "solution_statement": "Built a premium responsive landing page featuring smooth scrolling animations, dynamic scheduler widgets, and structured contact forms.",
            "results_statement": "Completed in 3 weeks. Online membership sign-up inquiries increased by 50% within 30 days of launch.",
            "technology_stack": "HTML5, CSS3, Tailwind CSS, JS, Gsap, AOS, Django",
            "project_duration": "3 Weeks",
            "tags": "Fitness, Landing Page, Animations, Tailwind",
            "is_featured": True
        },
        {
            "title": "UrbanNest - Real Estate Agency Website",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?auto=format&fit=crop&w=800&q=80",
            "client_name": "UrbanNest Realty",
            "industry": "Real Estate / Brokerage",
            "problem_statement": "The agency struggled to display properties beautifully with clear locations, which resulted in low lead volumes on mobile devices.",
            "solution_statement": "Developed a responsive property directory website, incorporating Mapbox GL JS map clustering to display local listings dynamically.",
            "results_statement": "Completed in 4 weeks. Search speed accelerated by 80% on mobile, boosting monthly listing inquiries by 110%.",
            "technology_stack": "HTML5, CSS3, Tailwind CSS, Mapbox API, Django, PostgreSQL",
            "project_duration": "4 Weeks",
            "tags": "Real Estate, Mapbox, Directory, Django",
            "is_featured": True
        },
        {
            "title": "VibeEvents - Ticket Booking & Event Platform",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1511578314322-379afb476865?auto=format&fit=crop&w=800&q=80",
            "client_name": "VibeEvents Group",
            "industry": "Entertainment & Events",
            "problem_statement": "VibeEvents needed an accessible ticketing application capable of processing thousands of ticket sales during event launches.",
            "solution_statement": "Developed a fast Django ticketing application, integrating Stripe webhooks to instantly process payments and generate unique PDF tickets.",
            "results_statement": "Processed 10,000+ tickets in under 5 minutes with zero transaction failures.",
            "technology_stack": "HTML5, Tailwind CSS, Django, Stripe, Weasyprint",
            "project_duration": "8 Weeks",
            "tags": "Ticketing, Stripe, Web App, Django",
            "is_featured": False
        },
        {
            "title": "ScholarGrid - Symmetric Academic LMS Platform",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
            "client_name": "ScholarGrid Academics",
            "industry": "EdTech / Education",
            "problem_statement": "ScholarGrid needed a responsive learning management system to host video assets and track student progress without system halts.",
            "solution_statement": "We implemented a custom Django LMS. We structured relational progress trackers and configured Gunicorn process isolation to manage concurrent user requests.",
            "results_statement": "Successfully hosted 5,00,000+ concurrent students with zero server latency issues. Retained 99.9% uptime.",
            "technology_stack": "Python, Django, PostgreSQL, Celery, Gunicorn, Redis",
            "project_duration": "12 Weeks",
            "tags": "LMS, EdTech, PostgreSQL, Django",
            "is_featured": False
        },
        {
            "title": "GrandVista - Hotel Reservation PMS Platform",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=800&q=80",
            "client_name": "GrandVista Resorts",
            "industry": "Hospitality & Tourism",
            "problem_statement": "GrandVista needed a booking portal to coordinate reservations across 5 properties in a unified panel.",
            "solution_statement": "Developed a custom property management system using Django, with PostgreSQL database configurations and multi-property managers.",
            "results_statement": "Consolidated booking operations. Direct room reservations increased by 35%.",
            "technology_stack": "Python, Django, PostgreSQL, Bootstrap 5, Gunicorn",
            "project_duration": "10 Weeks",
            "tags": "Hotel Booking, Hospitality, PostgreSQL, Django",
            "is_featured": False
        },
        {
            "title": "SwiftDrop - Logistics Tracking Mobile App Backend",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
            "client_name": "SwiftDrop Logistics",
            "industry": "Logistics & Delivery",
            "problem_statement": "SwiftDrop needed a mobile tracking system to connect customers, dispatchers, and drivers with real-time location coordinate updates.",
            "solution_statement": "GrowthSpare designed a clean Django REST Framework backend as an API Gateway, and built a cross-platform mobile application utilizing Flutter.",
            "results_statement": "Achieved sub-50ms API transition times. Driver routing accuracy increased by 30%.",
            "technology_stack": "Flutter, Dart, Django REST Framework, SimpleJWT, Redis",
            "project_duration": "12 Weeks",
            "tags": "Mobile App, Flutter, API, Logistics",
            "is_featured": False
        },
        {
            "title": "SafeInspected - Property Inspection Mobile Compliance",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1512403754473-278556139b6a?auto=format&fit=crop&w=800&q=80",
            "client_name": "SafeInspected Corp",
            "industry": "Real Estate / Compliance",
            "problem_statement": "Inspectors struggled to log compliance checklists offline while auditing remote properties.",
            "solution_statement": "Built a robust Flutter app utilizing local SQLite storage that automatically synchronizes with our Django API when internet reconnects.",
            "results_statement": "Enabled 100% offline inspection operations. Auditing report times decreased by 50%.",
            "technology_stack": "Flutter, Dart, Django REST Framework, SQLite, PostgreSQL",
            "project_duration": "8 Weeks",
            "tags": "Offline Sync, Flutter, Mobile App, API",
            "is_featured": False
        },
        {
            "title": "IndoBulk - Wholesale Procurement Portal System",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=800&q=80",
            "client_name": "IndoBulk Traders",
            "industry": "Manufacturing / Logistics",
            "problem_statement": "IndoBulk managed bulk wholesale orders manually via spreadsheets, causing coordination bottlenecks and delayed order processing.",
            "solution_statement": "We developed a secure B2B procurement portal on Django, featuring bulk inventory grids and invoice PDF generation.",
            "results_statement": "Order processing cycle shortened from 3 days to 4 hours. Automated billing accuracy reached 100%.",
            "technology_stack": "Python, Django, PostgreSQL, Alpine.js, Weasyprint",
            "project_duration": "12 Weeks",
            "tags": "B2B Portal, Procurement, Weasyprint, Django",
            "is_featured": False
        },
        {
            "title": "TechVibe - Subscription Content Media Publisher",
            "cat_obj": cat_web,
            "featured_image": "https://images.unsplash.com/photo-1504711434969-e33886168f5c?auto=format&fit=crop&w=800&q=80",
            "client_name": "TechVibe Media",
            "industry": "Media & Publishing",
            "problem_statement": "The publisher needed a fast-loading platform to restrict high-value articles behind a secure paywall.",
            "solution_statement": "We configured a custom publishing layout on Django. We integrated Stripe webhooks to manage monthly paywall subscriptions securely.",
            "results_statement": "Sub-180ms page load speeds. Monthly subscription revenue increased by 110%.",
            "technology_stack": "HTML5, Tailwind CSS, Django, Stripe, PostgreSQL, Redis",
            "project_duration": "8 Weeks",
            "tags": "Paywall, Subscriptions, Stripe, Django",
            "is_featured": False
        },

        # --- AI Automation (2 projects) ---
        {
            "title": "WhatsApp Lead Collection Bot for Local Retailer",
            "cat_obj": cat_ai,
            "featured_image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
            "client_name": "Vanguard Supplies",
            "industry": "Retail / Wholesale",
            "problem_statement": "The business processed bulk order requests manually over chat, leading to missed client briefs and slow quotation times.",
            "solution_statement": "Developed a secure, event-driven WhatsApp Cloud API webhook receiver that automatically processes incoming queries, registers contact data, and routes leads.",
            "results_statement": "Completed in 3 weeks. Automated lead qualification lowered lead drop-off rates by 38% and expedited quotation cycles.",
            "technology_stack": "Python, Django, Meta API, Redis, Celery, PostgreSQL",
            "project_duration": "3 Weeks",
            "tags": "WhatsApp, Webhooks, Automation, Python",
            "is_featured": True
        },
        {
            "title": "AI Customer Support Chatbot for E-Commerce",
            "cat_obj": cat_ai,
            "featured_image": "https://images.unsplash.com/photo-1531747118685-ca8fa6e08806?auto=format&fit=crop&w=800&q=80",
            "client_name": "ShopHub Retail",
            "industry": "E-Commerce",
            "problem_statement": "ShopHub faced high ticket volumes, causing their technical support staff to spend 50% of their time resolving repetitive, basic shipping status queries.",
            "solution_statement": "We engineered an autonomous AI Support Agent. We used LangChain, OpenAI API, and Celery task queues to automatically parse tickets, execute diagnostics, and reply to customers.",
            "results_statement": "Completed in 4 weeks. Automatically resolved 40% of baseline customer support queries, letting support agents handle critical issues.",
            "technology_stack": "Python, Django, OpenAI API, LangChain, Redis, Celery",
            "project_duration": "4 Weeks",
            "tags": "AI Chatbot, LangChain, Support, Python",
            "is_featured": True
        },

        # --- CRM & SaaS Solutions (2 projects) ---
        {
            "title": "BrightAcademy - School Management CRM",
            "cat_obj": cat_crm,
            "featured_image": "https://images.unsplash.com/photo-1501504905252-473c47e087f8?auto=format&fit=crop&w=800&q=80",
            "client_name": "BrightAcademy Schools",
            "industry": "Education / EdTech",
            "problem_statement": "BrightAcademy faced system errors and manual delay when coordinating student registers, marksheets, and parent feedback schedules.",
            "solution_statement": "GrowthSpare designed a clean, multi-tenant academic CRM on Django, with secure relational schemas and separate manager/parent access groups.",
            "results_statement": "Completed in 8 weeks. Successfully centralized operations, dropping student mark logging delay times by 75%.",
            "technology_stack": "Python, Django, PostgreSQL, Bootstrap 5, Chart.js",
            "project_duration": "8 Weeks",
            "tags": "CRM, School, Dashboard, Django",
            "is_featured": True
        },
        {
            "title": "SalesFlow - B2B Lead Management CRM",
            "cat_obj": cat_crm,
            "featured_image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80",
            "client_name": "SalesFlow Solutions",
            "industry": "B2B Sales",
            "problem_statement": "The sales team manually tracked 5,000 active pipeline leads over scattered spreadsheets, causing missing follow-ups and lost revenue.",
            "solution_statement": "We developed a private, secure, role-based CRM on Django, featuring user activity streams, clean performance charts, and direct contact integration.",
            "results_statement": "Completed in 6 weeks. Completely bypassed monthly third-party SaaS fees, and improved team conversion metrics by 30%.",
            "technology_stack": "Python, Django, PostgreSQL, Chart.js, HTML5, Tailwind CSS",
            "project_duration": "6 Weeks",
            "tags": "SaaS, CRM, Sales, Lead Tracking",
            "is_featured": True
        },

        # --- Digital Marketing (1 project) ---
        {
            "title": "Social Media Growth Campaign for Local Cafe",
            "cat_obj": cat_growth,
            "featured_image": "https://images.unsplash.com/photo-1554134678-e076c223a692?auto=format&fit=crop&w=800&q=80",
            "client_name": "MochaVibe Cafe",
            "industry": "Hospitality & PR",
            "problem_statement": "MochaVibe Cafe struggled to attract local customers during weekdays, relying heavily on low-margin aggregator discounts.",
            "solution_statement": "GrowthSpare executed a targeted social media growth campaign, developing professional vector graphics, local ads, and localized community reach funnels.",
            "results_statement": "Completed in 4 weeks. Weekday customer footfall increased by 35% within 30 days of launch, growing brand authority locally.",
            "technology_stack": "Meta Ads Manager, GTM, GA4, Adobe Illustrator, Canva",
            "project_duration": "4 Weeks",
            "tags": "SMM, Local Ads, Graphic Design, Marketing",
            "is_featured": True
        },

        # --- SEO Optimization (1 project) ---
        {
            "title": "Local SEO Optimization for Dental Clinic",
            "cat_obj": cat_seo,
            "featured_image": "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?auto=format&fit=crop&w=800&q=80",
            "client_name": "SmileDent Clinic",
            "industry": "Healthcare & Dentistry",
            "problem_statement": "SmileDent was spending heavily on Google Ads for local patients because their organic ranking was non-existent on Google Maps.",
            "solution_statement": "We implemented a technical SEO turnaround: optimized semantic HTML layout tags, integrated dynamic JSON-LD schemas, and improved on-page speed.",
            "results_statement": "Completed in 4 weeks. Clinic rankings climbed to top 3 on Google Maps, increasing organic patient bookings by 80%.",
            "technology_stack": "Google Search Console, GA4, Schema.org, Ahrefs, HTML5",
            "project_duration": "4 Weeks",
            "tags": "SEO, local SEO, Schema, Healthcare",
            "is_featured": True
        }
    ]

    for p_data in portfolio_projects_data:
        cat_obj = p_data.pop("cat_obj")
        title = p_data.pop("title")
        project, _ = Project.objects.update_or_create(title=title, defaults=p_data)
        project.categories.add(cat_obj)  # Map multiple categories using Many-to-Many dynamic methods [1]

    print(f"-> Successfully seeded {Project.objects.count()} customized case studies.")

    # ==============================================================================
    # 4. SEED EXACTLY 20 DYNAMIC BLOG INSIGHTS (4 per Category)
    # ==============================================================================
    print("-> Seeding Blog Categories...")

    def _get_or_create_blog_category(name, slug):
        obj, _ = BlogCategory.objects.update_or_create(slug=slug, defaults={"name": name})
        return obj

    bc_web = _get_or_create_blog_category("Website Development", "website-development")
    bc_ai = _get_or_create_blog_category("AI Automation", "ai-automation")
    bc_saas = _get_or_create_blog_category("CRM & SaaS Solutions", "crm-saas-solutions")
    bc_growth = _get_or_create_blog_category("Digital Marketing", "digital-marketing")
    bc_seo = _get_or_create_blog_category("SEO Optimization", "seo-optimization")
    bc_crm = bc_saas  # Define alias to safely prevent name errors during lookup [1]

    print("-> Seeding exactly 20 rich blog articles (4 per Category) with high-res Unsplash photos...")
    blogs_data = [
        # Website Development (4 items)
        {
            "title": "Optimizing Database Performance in Django 6.0 Applications",
            "category": bc_web,
            "featured_image": "https://images.unsplash.com/photo-1544383835-bda2bc66a55d?auto=format&fit=crop&w=800&q=80",
            "content": "<p>When building enterprise web applications, inefficient database query execution is often the root cause of high latency. Learn how to optimize Django ORM lookups by enforcing indexes and leveraging select_related.</p>",
            "tags": "Django, Database, Performance",
            "is_published": True,
            "is_featured": True
        },
        {
            "title": "Technical SEO Checklist for Sub-300ms Django Page Speeds",
            "category": bc_web,
            "featured_image": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Organic search optimization relies heavily on raw page performance. Learn how to compress static resources using Brotli, optimize CSS layouts, and structure schemas to score 100 on Lighthouse audits.</p>",
            "tags": "SEO, Django, Performance",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "A Guide to Secure JWT Token Authentication in REST APIs",
            "category": bc_web,
            "featured_image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Secure your stateless API endpoints. Learn how JSON Web Tokens work, configure expiration limits, and handle token rotation safely to protect user authorization data.</p>",
            "tags": "Security, JWT, REST API",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Flutter vs React Native: Choosing the Right Mobile Stack for 2026",
            "category": bc_web,
            "featured_image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Choosing the right mobile stack is crucial for long-term scalability. We compare Dart-based Flutter compilations with React Native's bridge framework for enterprise mobile applications.</p>",
            "tags": "Mobile, Flutter, React Native",
            "is_published": True,
            "is_featured": False
        },

        # AI Automation (4 items)
        {
            "title": "How to Securely Connect WhatsApp Cloud API with Django Webhooks",
            "category": bc_ai,
            "featured_image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Integrating the WhatsApp Cloud API with Django requires robust webhook processing. We discuss verifying request signatures, validating payloads, and handling asynchronous execution with Celery.</p>",
            "tags": "WhatsApp, Webhooks, Celery",
            "is_published": True,
            "is_featured": True
        },
        {
            "title": "Unlocking B2B Conversions: The Power of Conversational AI Chatbots",
            "category": bc_ai,
            "featured_image": "https://images.unsplash.com/photo-1531747118685-ca8fa6e08806?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Explore how conversational AI chatbots process user intent to qualify and route leads. By connecting chat streams directly with your database, you can dramatically scale sales funnels.</p>",
            "tags": "AI, Chatbots, LeadGen",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "How to Securely Integrate OpenAI GPT-4o into Your ERP Workflows",
            "category": bc_ai,
            "featured_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Enterprise AI integration requires strict privacy compliance. Learn how to securely pass raw workflow structures into OpenAI endpoints without exposing sensitive company data.</p>",
            "tags": "AI, OpenAI, ERP, Automation",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Implementing Retrieval-Augmented Generation (RAG) with PGVector",
            "category": bc_ai,
            "featured_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Retrieval-Augmented Generation lets your AI query custom knowledge bases. We guide you through chunking documents, creating vector embeddings, and indexing them using PGVector in PostgreSQL.</p>",
            "tags": "RAG, PGVector, LLM, Python",
            "is_published": True,
            "is_featured": False
        },

        # CRM & SaaS Solutions (4 items)
        {
            "title": "Architecting Multi-Tenant SaaS Databases in PostgreSQL",
            "category": bc_crm,
            "featured_image": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Multi-tenancy requires strict isolation boundaries. We evaluate shared database/isolated schema models and compare PostgreSQL's performance metrics for heavy SaaS usage.</p>",
            "tags": "SaaS, PostgreSQL, Database",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Why Proprietary CRMs Outperform Off-The-Shelf SaaS Platforms",
            "category": bc_crm,
            "featured_image": "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Off-the-shelf software is rarely optimized for your unique sales workflow. Learn how custom, private CRM platforms eliminate seat licensing costs and keep you in control of your data.</p>",
            "tags": "CRM, Custom Software, SaaS",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Designing Clean Figma User Journeys for Complex SaaS Dashboards",
            "category": bc_crm,
            "featured_image": "https://images.unsplash.com/photo-1542744094-3a31f103e35f?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Complex dashboard layouts require intuitive UX research. Learn how to wireframe smooth user journeys, plan clean grid structures, and ensure high developer-handoff accuracy in Figma.</p>",
            "tags": "UI UX, Figma, Product Design",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Deploying Multi-Tenant Invoicing Engines with Stripe Webhooks",
            "category": bc_crm,
            "featured_image": "https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Stripe webhooks are essential for automated subscription management. Learn how to process billing notifications, handle renewals, and manage multi-tenant access tiers safely.</p>",
            "tags": "Stripe, Webhooks, SaaS, Invoicing",
            "is_published": True,
            "is_featured": False
        },

        # Digital Marketing (4 items)
        {
            "title": "Creating Unified Brand Identity Kits and Guidelines",
            "category": bc_growth,
            "featured_image": "https://images.unsplash.com/photo-1611162617213-7d7a39e9b1d7?auto=format&fit=crop&w=800&q=80",
            "content": "<p>A brand kit is a promise of quality. GrowthSpare builds high-fidelity vector guidelines, establishing responsive typography hierarchies and semantic color palettes.</p>",
            "tags": "Brand Guide, Design Tokens, Vector, Figma",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "High-Conversion Programmatic Graphic Layout Designs",
            "category": bc_growth,
            "featured_image": "https://images.unsplash.com/photo-1542744094-3a31f103e35f?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Our graphic designers compile professional assets. We create high-resolution vectors, ad creative pools, and responsive assets designed to drive CTR in pay-per-click campaigns.</p>",
            "tags": "Graphic, Ad Creative, Banner, Design",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Why Professional Graphic Asset Sets Maximize Social Ads CTR",
            "category": bc_growth,
            "featured_image": "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Stop burning budget on standard, non-converting social ads. Learn how highly targeted ad groups, negative keywords, and precise conversion pixels secure high-value sales.</p>",
            "tags": "PPC, Google Ads, Ad Spend, CRO",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Conversion Rate Optimization (CRO) Best Practices for B2B Funnels",
            "category": bc_growth,
            "featured_image": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Attracting traffic is only half the battle. Discover how to execute detailed A/B tests, restructure forms, and optimize micro-copy to maximize lead ingestion rates.</p>",
            "tags": "Marketing, CRO, Conversion, B2B",
            "is_published": True,
            "is_featured": False
        },

        # SEO Optimization (4 items)
        {
            "title": "Maximize Google Ads ROI: B2B Conversion Tracking Best Practices",
            "category": bc_seo,
            "featured_image": "https://images.unsplash.com/photo-1432821596592-e2c18b78144f?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Stop wasting ad spend. Learn how to configure Google Tag Manager and exact conversion tracking pixels to accurately measure high-intent search ad ROI.</p>",
            "tags": "PPC, Google Ads, GA4",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Meta Conversions API (CAPI) Integration Guide for High-ROI Ad Spend",
            "category": bc_seo,
            "featured_image": "https://images.unsplash.com/photo-1551836022-d5d88e9218df?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Ad-blockers and browser updates block client-side tracking pixels. Learn how to integrate Meta's server-side Conversions API (CAPI) to record accurate attribution metrics.</p>",
            "tags": "Meta Ads, Conversion API, Marketing",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "The Anatomy of a High-Converting B2B Landing Page in Tailwind CSS",
            "category": bc_seo,
            "featured_image": "https://images.unsplash.com/photo-1551434678-e076c223a692?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Conversion psychology is key to landing page success. Learn how to structure visual flows, implement async forms, and design clear CTAs using Tailwind CSS for high conversion rates.</p>",
            "tags": "Tailwind CSS, Landing Page, CRO",
            "is_published": True,
            "is_featured": False
        },
        {
            "title": "Keyword Intent Mapping: The Secret to High-Conversion SEO Campaigns",
            "category": bc_seo,
            "featured_image": "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?auto=format&fit=crop&w=800&q=80",
            "content": "<p>Targeting traffic is easy, but targeting conversion is hard. Learn how to audit user search intent, separate informational queries from transactional keywords, and structure high-converting content.</p>",
            "tags": "SEO, Keywords, CRO, Google",
            "is_published": True,
            "is_featured": False
        }
    ]

    for b_data in blogs_data:
        title = b_data.pop("title")
        BlogPost.objects.update_or_create(title=title, defaults={**b_data, "author": author})
    print(f"-> Successfully seeded {len(blogs_data)} blog publications.")

    # ==============================================================================
    # 5. SEED EXACTLY 50 GLOBAL FAQS (10 items per Category matching our 5 Divisions)
    # ==============================================================================
    print("-> Seeding FAQ Categories...")

    def _get_or_create_faq_category(name, slug, order):
        obj, _ = FAQCategory.objects.update_or_create(
            slug=slug, defaults={"name": name, "order": order}
        )
        return obj

    f_cat_web = _get_or_create_faq_category("Website Development", "website-development", 1)
    f_cat_ai = _get_or_create_faq_category("AI Automation", "ai-automation", 2)
    f_cat_saas = _get_or_create_faq_category("CRM", "crm", 3)
    f_cat_growth = _get_or_create_faq_category("Digital Marketing", "digital-marketing", 4)
    f_cat_seo = _get_or_create_faq_category("SEO Optimization", "seo-optimization", 5)
    f_cat_mkt = f_cat_seo  # Define alias to safely prevent name errors during lookup [1]

    faqs_data = [
        # 1. Website Development (10 FAQs)
        {"category": f_cat_web, "question": "How long does it take to build a website?", "answer": "A standard, responsive brochure website can launch within 3 to 4 weeks. Highly specialized web applications and SaaS development milestones average between 2 to 3 months depending on complexity.", "order": 1},
        {"category": f_cat_web, "question": "Why is a semantic HTML structure important for my website?", "answer": "Semantic HTML helps search engines like Google understand your content's hierarchy, which is essential to achieving rich indexing and higher organic SEO ranks.", "order": 2},
        {"category": f_cat_web, "question": "How do you optimize mobile page rendering speeds?", "answer": "We compress and convert static assets (images, vectors) to modern formats like WebP, implement lazy loading, and use Brotli static compression to speed up load times.", "order": 3},
        {"category": f_cat_web, "question": "Do you support cross-platform mobile application development?", "answer": "Yes, we develop cross-platform mobile apps for iOS and Android using Flutter, which we connect to secure, high-speed Django REST Framework backends.", "order": 4},
        {"category": f_cat_web, "question": "What database systems are deployed with Web Solutions?", "answer": "We use PostgreSQL for secure, multi-row relational transactions in production, and SQLite for quick local development environments.", "order": 5},
        {"category": f_cat_web, "question": "How do you guarantee a 95+ score on Core Web Vitals?", "answer": "We audit system code carefully: minimize blocking scripts, defer non-critical JS, inline crucial styling rules, and optimize image rendering configurations.", "order": 6},
        {"category": f_cat_web, "question": "Do you provide custom API integrations with third-party software?", "answer": "Yes, we develop secure RESTful and GraphQL API gateways that allow your custom web systems to connect and synchronize with external software platforms.", "order": 7},
        {"category": f_cat_web, "question": "What is the typical project development workflow?", "answer": "We follow a 4-stage process: discovery & wireframing, backend schema development, frontend template assembly, and final containerized deployment & testing.", "order": 8},
        {"category": f_cat_web, "question": "Can I edit and manage page content without developer assistance?", "answer": "Yes. Our Django sites integrate cleanly with the custom Admin Console, letting you edit services, case studies, blogs, and FAQs easily.", "order": 9},
        {"category": f_cat_web, "question": "Do your websites comply with international accessibility standards?", "answer": "Yes, all our frontend templates are built to meet WCAG AA accessibility requirements, ensuring compatibility with screen readers and mobile systems.", "order": 10},

        # 2. AI Automation (10 FAQs)
        {"category": f_cat_ai, "question": "How does WhatsApp Cloud API webhook processing work?", "answer": "Our Django servers act as webhook receivers that process incoming WhatsApp events in real-time, matching contact data and triggering auto-responses.", "order": 21},
        {"category": f_cat_ai, "question": "Is client data kept private when using OpenAI endpoints?", "answer": "Yes, we utilize enterprise API connections that enforce strict data-privacy policies, meaning your data is never used to train public models.", "order": 22},
        {"category": f_cat_ai, "question": "What is a Retrieval-Augmented Generation (RAG) system?", "answer": "RAG connects secure vector databases containing your company's proprietary documents with an LLM, allowing accurate, context-aware AI search.", "order": 23},
        {"category": f_cat_ai, "question": "Can AI agents automate invoicing and billing tasks?", "answer": "Yes, we use OCR and LLMs to automatically parse invoices, validate purchase orders, and sync data directly with your custom ERP database.", "order": 24},
        {"category": f_cat_ai, "question": "How do you handle conversational context in AI Chatbots?", "answer": "We design stateful database pipelines that track and pass user session histories, letting our AI assistants hold natural, multi-turn conversations.", "order": 25},
        {"category": f_cat_ai, "question": "Can WhatsApp automations scale to handle heavy traffic?", "answer": "Yes, we offload message queues to Celery and Redis, allowing our servers to process thousands of incoming webhooks concurrently without delay.", "order": 26},
        {"category": f_cat_ai, "question": "Do you support fine-tuning of open-source models?", "answer": "Yes, we configure and fine-tune open-source models like Llama and Mistral for specific corporate guidelines, hosting them on private clouds.", "order": 27},
        {"category": f_cat_ai, "question": "How do you prevent AI assistants from hallucinating?", "answer": "We implement strict system parameters, set temperature levels near 0, and use RAG structures to restrict answers to verified documentation.", "order": 28},
        {"category": f_cat_ai, "question": "Can AI automations connect with my existing CRM?", "answer": "Yes, we build secure webhook receivers and custom API connectors to sync lead details and interaction logs with your CRM automatically.", "order": 29},
        {"category": f_cat_ai, "question": "Do you write custom models for predictive sales analysis?", "answer": "Yes, we implement custom Python data pipelines using Pandas and Scikit-Learn to analyze historical customer interactions and predict sales trends.", "order": 30},

        # 3. CRM (10 FAQs)
        {"category": f_cat_saas, "question": "What is the difference between a custom CRM and an off-the-shelf tool?", "answer": "A custom CRM is built around your specific pipeline, team roles, and invoicing methods, keeping you in complete control of your data without seat license fees.", "order": 31},
        {"category": f_cat_saas, "question": "How do you enforce database security in multi-tenant SaaS?", "answer": "We implement strict schema-level data separation in PostgreSQL. This isolates each tenant's customer data, preventing unauthorized crossover access.", "order": 32},
        {"category": f_cat_saas, "question": "Can we manage subscription billing and invoices inside the SaaS portal?", "answer": "Yes, we configure Stripe or Razorpay webhook integrations to automate invoice generation, billing cycles, and subscription renewals.", "order": 33},
        {"category": f_cat_saas, "question": "How do you implement Role-Based Access Control (RBAC) inside CRM dashboards?", "answer": "We establish strict Django group permissions to define what sections (Leads, Invoices, User directories) are visible to Admins, Managers, or Clients.", "order": 34},
        {"category": f_cat_saas, "question": "Can our sales teams export data reports to CSV/Excel formats?", "answer": "Yes, our custom admin dashboards include dynamic exporting, allowing you to generate and download Excel or CSV reports for specific timeframes.", "order": 35},
        {"category": f_cat_saas, "question": "What backend tools do you recommend to run SaaS schedulers?", "answer": "We configure Celery and Redis to handle recurring background tasks like monthly invoicing, subscription checks, and reports generation safely.", "order": 36},
        {"category": f_cat_saas, "question": "Do custom ERPs support automated stock and warehouse tracking?", "answer": "Yes, we design real-time database tracking tables that automatically log stock valuations, material dispatches, and incoming wholesale supplies.", "order": 37},
        {"category": f_cat_saas, "question": "Are user passwords encrypted in our custom database?", "answer": "Yes. We use Django's built-in secure hashing algorithms (PBKDF2 with SHA-256) to encrypt and protect all user passwords from compromise.", "order": 38},
        {"category": f_cat_saas, "question": "Can custom CRMs automate follow-up emails and SMS alerts?", "answer": "Yes, we write custom webhook tasks that can automatically dispatch transactional emails or Twilio SMS updates to leads at specific pipeline stages.", "order": 39},
        {"category": f_cat_saas, "question": "What is the typical infrastructure cost of hosting a custom SaaS?", "answer": "By using lightweight, containerized Docker environments, hosting typically starts as low as $10-$20/mo on managed VPS clouds like DigitalOcean.", "order": 40},

        # 4. Digital Marketing (10 FAQs)
        {"category": f_cat_growth, "question": "Why are unified design guidelines and brand kits valuable?", "answer": "Establishing consistent design tokens and brand guidelines ensures your business communicates high visual authority globally across all channels.", "order": 41},
        {"category": f_cat_growth, "question": "Do your graphic design vectors support high-resolution print exports?", "answer": "Yes, we design all vector brand assets and typography guides in scalable SVG formats, allowing crisp high-resolution exports for any display or print system.", "order": 42},
        {"category": f_cat_growth, "question": "How do professional ad designs improve campaign performance?", "answer": "We create targeted vector ad graphics that capture visual interest, helping to maximize your click-through rates (CTR) and decrease cost per acquisition (CPA).", "order": 43},
        {"category": f_cat_growth, "question": "Do you design custom typography and font pairings?", "answer": "Yes, we establish semantic corporate font systems, optimizing readability and interface flows across landing screens.", "order": 44},
        {"category": f_cat_growth, "question": "How do you manage company brand guidebooks?", "answer": "We deliver comprehensive PDF brand manuals that outline logo safety margins, palette guidelines, and exact spacing tokens.", "order": 45},
        {"category": f_cat_growth, "question": "Can your team design custom slide deck assets for sales presentations?", "answer": "Yes, we create corporate pitch decks and marketing presentations aligned to your company's design system.", "order": 46},
        {"category": f_cat_growth, "question": "How do you prepare image assets to ensure fast page load speeds?", "answer": "We optimize and compress all graphics to modern web formats (WebP/SVG), keeping image file sizes minimal for faster performance.", "order": 47},
        {"category": f_cat_growth, "question": "What tools do you use to map out user journeys?", "answer": "We use Figma to research, test, and design interactive user flows and UX prototypes.", "order": 48},
        {"category": f_cat_growth, "question": "Can I request custom vector assets for my software interface?", "answer": "Yes, we design custom vector icons and responsive interface assets tailored specifically to match your SaaS dashboard's styling.", "order": 49},
        {"category": f_cat_growth, "question": "Do you offer marketing template packages for B2B channels?", "answer": "Yes, we design custom social media templates and ad sets in Figma, enabling your marketing team to scale campaign creatives easily.", "order": 50},

        # 5. SEO Optimization (10 FAQs)
        {"category": f_cat_mkt, "question": "How do you achieve top positions on search engines?", "answer": "We focus on a comprehensive SEO strategy: we optimize semantically-sound HTML, build structured JSON-LD schemas, and audit site speed.", "order": 51},
        {"category": f_cat_mkt, "question": "What is a JSON-LD structured data schema?", "answer": "It is a standardized script format that helps search engines understand your content, helping your site secure rich snippets in search results.", "order": 52},
        {"category": f_cat_mkt, "question": "Do you set up GA4 Google Analytics tracking?", "answer": "Yes, we integrate Google Analytics 4 (GA4) and Google Tag Manager (GTM) to track conversion funnels and user paths accurately.", "order": 53},
        {"category": f_cat_mkt, "question": "How do you optimize Google Ads pay-per-click spend?", "answer": "We restructure your ad groups: target exact-match, high-intent keywords, eliminate non-converting terms, and set up conversion tracking.", "order": 54},
        {"category": f_cat_mkt, "question": "What is the Meta Conversions API (CAPI)?", "answer": "It is a server-side tracking tool that bypasses browser-based ad-blockers, sending accurate conversion data directly to Meta's servers.", "order": 55},
        {"category": f_cat_mkt, "question": "How do you grow B2B engagement on LinkedIn?", "answer": "We design structured content schedules and educational carousels that address specific pain points, establishing your brand's authority.", "order": 56},
        {"category": f_cat_mkt, "question": "Do you design landing pages for high-intent campaigns?", "answer": "Yes, we build high-converting, single-page landing structures optimized for speed and clear call-to-actions, maximizing campaign ROI.", "order": 57},
        {"category": f_cat_mkt, "question": "How do you analyze competitor keywords?", "answer": "We use advanced technical tools to analyze competitor rankings, identify search volume opportunities, and target valuable keywords.", "order": 58},
        {"category": f_cat_mkt, "question": "What is the average click-through rate (CTR) of your campaigns?", "answer": "By pairing targeted copywriting with clean, fast landing pages, our paid ad campaigns average CTRs above 8% for search ads.", "order": 59},
        {"category": f_cat_mkt, "question": "Can I track my organic SEO results in real-time?", "answer": "Yes, we configure and share live, transparent Google Search Console and Analytics dashboards, letting you monitor ranking progress.", "order": 60}
    ]

    for f_data in faqs_data:
        question = f_data.pop("question")
        FAQItem.objects.update_or_create(question=question, defaults=f_data)
    print(f"-> Successfully seeded exactly {len(faqs_data)} FAQ items.")

    # ==============================================================================
    # 6. SEED TESTIMONIALS
    # ==============================================================================
    print("-> Seeding Client Testimonials...")

    # Dynamic testimonials for realistic projects with custom markers [1]
    testimonials_data = [
        {
            "client_name": "Mirza Khalique Beg",
            "company_name": "Elevate Workforce LLC",
            "designation": "Operations Director",
            "review": "[Sample Review] GrowthSpare IT Solutions successfully re-engineered our SaaS deployment schemas. The team configured a highly-performant, secure database cluster that scaled past our peak concurrent user demands without any downtime.",
            "rating": 5,
            "is_active": True,
            "order": 1
        },
        {
            "client_name": "Aarav Sharma",
            "company_name": "EduLearn Academy",
            "designation": "Managing Director",
            "review": "[Example Testimonial] The LMS platform is incredibly stable and fast. Our students have experienced zero downtime, and the admin system is simple and responsive.",
            "rating": 5,
            "is_active": True,
            "order": 2
        },
        {
            "client_name": "Siddharth Roy",
            "company_name": "BiteCraft Bistro",
            "designation": "Founder",
            "review": "[Demo Feedback] Our organic website conversions and table reservations increased significantly after Launching our new website.",
            "rating": 5,
            "is_active": True,
            "order": 3
        },
        {
            "client_name": "Dr. Ananya Patel",
            "company_name": "SmileDent Clinic",
            "designation": "Chief Surgeon",
            "review": "[Example Testimonial] The custom booking engine has significantly decreased front-desk call load. SMS reminders work like clockwork.",
            "rating": 5,
            "is_active": True,
            "order": 4
        },
        {
            "client_name": "Vikram Aditya",
            "company_name": "Apex Wealth Advisors",
            "designation": "Partner",
            "review": "[Sample Review] Highly secure corporate portal setup. Our document sharing is completely encrypted, ensuring peace of mind for our clients.",
            "rating": 5,
            "is_active": True,
            "order": 5
        },
        {
            "client_name": "Rohan Mehra",
            "company_name": "HomeFind Realty",
            "designation": "Director",
            "review": "[Demo Feedback] The dynamic Mapbox property search is outstandingly fast. Our real estate lead generation has doubled.",
            "rating": 5,
            "is_active": True,
            "order": 6
        },
        {
            "client_name": "Meera Sen",
            "company_name": "Urban Space Group",
            "designation": "Founder",
            "review": "[Example Testimonial] Excellent SEO campaign turnaround. Our organic search impressions grew by over 300% in a few months.",
            "rating": 5,
            "is_active": True,
            "order": 7
        },
    ]

    for t_data in testimonials_data:
        client_name = t_data.pop("client_name")
        company_name = t_data.pop("company_name")
        Testimonial.objects.update_or_create(
            client_name=client_name, company_name=company_name, defaults=t_data
        )
    print("-> Testimonials seeded successfully.")

    # ==============================================================================
    # 6B. SEED CLIENT/PARTNER LOGOS (Homepage "Trusted by" strip)
    # ==============================================================================
    print("-> Seeding Client Logos...")
    client_logo_names = [
        "DataCore Systems",
        "Arvex Retail",
        "Nexora Logistics",
        "Velunex Textiles",
        "Skyline Ventures",
        "Primeon Manufacturing",
    ]
    for index, name in enumerate(client_logo_names):
        # Logo ImageField is left blank on purpose: these are demo/placeholder
        # client names (no real company logos exist to license/display for
        # them), so the homepage template renders the premium static SVG
        # wordmark shipped under static/images/clients/ instead. Real clients
        # can have their actual logo uploaded here via the admin at any time,
        # which will automatically take priority over the static placeholder.
        ClientLogo.objects.update_or_create(
            name=name,
            defaults={"order": index, "is_active": True},
        )
    print("-> Client Logos seeded successfully.")

    # ==============================================================================
    # 7. SEED SYSTEM BROADCASTS & ANNOUNCEMENTS
    # ==============================================================================
    print("-> Seeding Active Dashboard Announcements...")

    SystemAnnouncement.objects.update_or_create(
        title="Welcome to your GrowthSpare Portal",
        defaults={
            "content": "Our engineering desk has initialized your secure workspace environment. "
                       "You can now monitor project milestones, review consultation status, and "
                       "retrieve API keys.",
            "target_role": "ALL",
            "created_by": author,
        },
    )
    print("-> Dashboard announcements seeded successfully.")

    print("\n✓ Dynamic 7-Division database seeding completed successfully!")
    print("==============================================================================")
    print("Seeding complete. Administrator credentials are managed via the "
          "SEED_ADMIN_USERNAME / SEED_ADMIN_EMAIL / SEED_ADMIN_PASSWORD "
          "environment variables and are not printed here for security.")
    print("==============================================================================")


if __name__ == "__main__":
    seed_all_data()