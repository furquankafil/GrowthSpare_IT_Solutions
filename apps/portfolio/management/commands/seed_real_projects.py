"""
Seeds the genuine GrowthSpare portfolio projects plus honest self-hosted visuals.

Idempotent: safe to re-run (upserts by slug, resets category links, repairs
legacy Unsplash/blank visuals by slug — never creates duplicates).

Honesty rules enforced here (see PORTFOLIO_IMPLEMENTATION_REPORT.md):
- The four live sites were verified against their live HTML on 2026-09-26
  (content sections) and their HTML source (technology stack). Only
  verified facts are stored — no metrics, reviews, ratings or awards.
- The CRM entries have NO public URL and only list capabilities already
  present in this workspace (contact lead capture, consultation pipeline
  with triage statuses, role-based dashboards, team directory, role
  announcements). They are tagged "private-project".
- The gaming entry has NO public URL and every listed area is framed as
  intended prototype scope, never as launched. Tagged "prototype".
- Repository audit (2026-09-26): no dedicated "Social Media CRM" module,
  model, migration, or history was found anywhere in the codebase. The
  "Social Media CRM" entry below is therefore scoped STRICTLY to the same
  workspace-present CRM capabilities as the Custom CRM (leads arriving via
  social/WhatsApp/website channels triaged in one pipeline). It claims no
  Meta API sync, no auto-posting, no sentiment analysis, no public URL,
  no users and no metrics. Status: Private Project / In Development.
- featured_image values are self-hosted SVG portfolio artwork under
  /static/images/portfolio/<slug>.svg (stylised mockups labelled
  "Illustrative portfolio visual" inside the artwork — never presented
  as live screenshots). No Unsplash hotlinks, no reused image across
  unrelated projects.

Uses Django's configured database (Supabase/Postgres in production via
DATABASE_URL) — no hardcoded SQLite anywhere.
"""

from django.core.management.base import BaseCommand

from apps.portfolio.models import Project, ProjectCategory


VISUAL_BASE = "https://growthspareitsolutions.com/static/images/portfolio"


def _get_or_create_category(name, slug):
    obj, _ = ProjectCategory.objects.update_or_create(
        slug=slug, defaults={"name": name}
    )
    return obj


PROJECTS = [
    # ------------------------------------------------------------------
    # 1. Bake Wonders — live bakery website (verified 2026-09-26)
    # ------------------------------------------------------------------
    {
        "slug": "bake-wonders",
        "title": "Bake Wonders",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/bake-wonders.svg",
        "video_url": None,
        "live_url": "https://endearing-piroshki-508bdd.netlify.app/",
        "client_name": "Bake Wonders",
        "industry": "Bakery / Food Business",
        "problem_statement": (
            "Bake Wonders is a home bakery selling cheesecakes, bomboloni, "
            "donuts and custom cakes in small daily batches. It needed a clean, "
            "mobile-friendly website that presents what is baked fresh each day, "
            "what can be made to order with clear pricing, and how to place an "
            "order — without the overhead of a full online store."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a single-page bakery website with "
            "four clear sections — Ready to Eat, Made to Order, Occasions & "
            "Chocolates, and Ordering Info. The page presents the daily menu "
            "(cheesecake slices, donuts, bomboloni, brownies, tres leches), the "
            "made-to-order range (classic cakes, red velvet, cheesecakes, "
            "cupcakes, bento cakes, dry cakes and pies) with half-kg pricing, "
            "occasion chocolates, and ordering terms. Ordering runs through "
            "Instagram (@bake_wonders_), with prominent calls-to-action in the "
            "header, hero and footer."
        ),
        "results_statement": (
            "Delivered and live: a fast, mobile-friendly one-page bakery website "
            "presenting the daily menu, the made-to-order range with pricing, "
            "occasion chocolates, ordering information and Instagram ordering. "
            "No performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Bakery, Food Business, Menu Website, Made-to-Order Cakes, "
            "Instagram Ordering, Responsive Website"
        ),
        "is_featured": True,
        "is_concept_project": False,
        "meta_title": "Bakery Website Development Project | GrowthSpare IT Solutions",
        "meta_description": (
            "Bake Wonders is a live bakery website by GrowthSpare IT Solutions "
            "presenting daily bakes, made-to-order cakes, cheesecakes, donuts "
            "and Instagram ordering."
        ),
    },
    # ------------------------------------------------------------------
    # 2. Social Frame Creative — live creative agency website
    # ------------------------------------------------------------------
    {
        "slug": "social-frame-creative",
        "title": "Social Frame Creative",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/social-frame-creative.svg",
        "video_url": None,
        "live_url": "https://socialcreatives.in/",
        "client_name": "Social Frame Creative",
        "industry": "Creative Agency / Brand Design",
        "problem_statement": (
            "Social Frame Creative is a creative agency offering brand strategy, "
            "brand identity, social media creatives, website design, UI/UX, "
            "creative content, digital marketing and AI creative solutions. It "
            "needed a premium agency website that positions the brand, explains "
            "its services, presents its work and creative process, answers "
            "common questions, and converts visitors into enquiries."
        ),
        "solution_statement": (
            "GrowthSpare built a multi-page creative agency website covering "
            "Home, About, Services, Our Work, Reviews and Contact, plus "
            "dedicated pages for eight service lines — Brand Strategy, Brand "
            "Identity, Social Media Creative, Website Design, UI/UX Design, "
            "Creative Content, Digital Marketing and AI Creative Solutions. The "
            "site presents the agency's positioning and vision, the industries "
            "it designs for, its creative standard and principles, a seven-step "
            "process, FAQs, and contact conversion via phone, email, WhatsApp "
            "and enquiry forms."
        ),
        "results_statement": (
            "Delivered and live: a premium multi-page creative agency website "
            "presenting brand positioning, eight service lines, work "
            "presentation, process, FAQs and contact conversion. The agency's "
            "own showcased samples are labelled as concept pieces on the live "
            "site; no client relationships, metrics or results are claimed here."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript",
        "project_duration": "Delivered",
        "tags": (
            "Creative Agency, Brand Identity, Social Media Creatives, UI/UX, "
            "Website Design, Digital Marketing"
        ),
        "is_featured": True,
        "is_concept_project": False,
        "meta_title": "Creative Agency Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "Social Frame Creative is a live creative agency website by "
            "GrowthSpare IT Solutions covering brand strategy, identity, social "
            "creatives and contact conversion."
        ),
    },
    # ------------------------------------------------------------------
    # 3. MAC INTERIO — live furniture manufacturer website
    # ------------------------------------------------------------------
    {
        "slug": "mac-interio",
        "title": "MAC INTERIO",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/mac-interio.svg",
        "video_url": None,
        "live_url": "https://mac-interio.netlify.app/",
        "client_name": "MAC INTERIO / Little Star",
        "industry": "Furniture Manufacturing / Interiors",
        "problem_statement": (
            "MAC INTERIO is a furniture manufacturer and interior furniture "
            "specialist in Kirti Nagar, New Delhi, with the Little Star showroom "
            "as its public face. It needed a premium website that presents its "
            "custom and modular furniture offering for residential, office and "
            "commercial spaces, shows representative work and gallery imagery, "
            "explains its process, and routes showroom visits and project "
            "enquiries."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a multi-page manufacturer website "
            "with Home, About, Services, Portfolio, Gallery and Contact "
            "sections. The site presents six service lines — Custom, Modular, "
            "Residential, Office and Commercial Furniture plus Interior "
            "Furniture Solutions — a five-step process (Understand, Design, "
            "Refine, Manufacture, Deliver), the Little Star showroom at "
            "Furniture Block, Kirti Nagar, and contact conversion via phone, "
            "email, WhatsApp and maps directions."
        ),
        "results_statement": (
            "Delivered and live: a premium furniture manufacturer website "
            "presenting six service lines, portfolio and gallery sections, "
            "process, showroom information and call/WhatsApp contact. The live "
            "site's portfolio slots are representative categories; no specific "
            "client projects, revenue or lead metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Furniture Manufacturer, Modular Furniture, Custom Furniture, "
            "Residential Furniture, Office Furniture, Kirti Nagar"
        ),
        "is_featured": True,
        "is_concept_project": False,
        "meta_title": "Furniture Website Development Project | GrowthSpare IT Solutions",
        "meta_description": (
            "MAC INTERIO is a live furniture manufacturer website by GrowthSpare "
            "IT Solutions for a Kirti Nagar maker covering custom, modular and "
            "interior furniture."
        ),
    },
    # ------------------------------------------------------------------
    # 4. Furniture Studio by Akdas — live custom furniture studio website
    # ------------------------------------------------------------------
    {
        "slug": "furniture-studio-by-akdas",
        "title": "Furniture Studio by Akdas",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/furniture-studio-by-akdas.svg",
        "video_url": None,
        "live_url": "https://furniture-studio-akdas.netlify.app/",
        "client_name": "Furniture Studio by Akdas",
        "industry": "Custom Furniture Studio",
        "problem_statement": (
            "Furniture Studio by Akdas is a custom furniture studio in Kirti "
            "Nagar, New Delhi, building made-to-measure sofas, beds, dining "
            "sets and chairs. It needed a premium studio website that presents "
            "the collection, explains how custom furniture works, shows "
            "selected work, documents the craft process, and converts visitors "
            "into quote requests via WhatsApp, phone or a studio visit."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a multi-page studio website with "
            "Home, About, Furniture, Custom, Projects, Process and Contact "
            "sections. The site presents the made-to-measure collection "
            "(sofas, beds and headboards, dining sets, lounge and accent "
            "chairs, centre tables), the custom workflow (measure, material, "
            "build), a six-step craft process through delivery and placement, "
            "selected work, material and detail notes, and conversion via "
            "WhatsApp, phone and directions to the Kirti Nagar studio."
        ),
        "results_statement": (
            "Delivered and live: a premium custom furniture studio website "
            "presenting the collection, custom workflow, craft process, "
            "selected work and studio contact. Close-up and social imagery on "
            "the live site is labelled illustrative; no customer claims, "
            "revenue or lead metrics are made here."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Custom Furniture Studio, Sofas, Beds, Dining Sets, Made-to-Measure, "
            "Kirti Nagar"
        ),
        "is_featured": True,
        "is_concept_project": False,
        "meta_title": "Custom Furniture Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "Furniture Studio by Akdas is a live custom furniture studio website "
            "by GrowthSpare IT Solutions covering sofas, beds, dining and "
            "made-to-measure builds."
        ),
    },
    # ------------------------------------------------------------------
    # 5. GrowthSpare Custom CRM — private internal project (NO public URL)
    # ------------------------------------------------------------------
    {
        "slug": "growthspare-custom-crm",
        "title": "GrowthSpare Custom CRM",
        "category_slugs": ["crm-saas-solutions"],
        "featured_image": f"{VISUAL_BASE}/growthspare-custom-crm.svg",
        "video_url": None,
        "live_url": None,
        "client_name": "GrowthSpare IT Solutions",
        "industry": "Internal Tools / CRM Software",
        "problem_statement": (
            "GrowthSpare needed an internal system to track website and "
            "consultation enquiries, manage the consultation pipeline from "
            "triage to completion, and give admins, managers and clients "
            "appropriate visibility — without paying per-seat fees for "
            "third-party CRM software."
        ),
        "solution_statement": (
            "The Custom CRM is being developed as a private internal platform "
            "on GrowthSpare's standard Django stack. It builds on capabilities "
            "already present in the GrowthSpare workspace: enquiry and lead "
            "capture with budget and service routing, a consultation booking "
            "pipeline with triage statuses (pending, scheduled, completed, "
            "cancelled), role-based dashboards showing account, lead and "
            "booking metrics with recent activity, a team and client directory "
            "with role-based access, and role-targeted announcements. There is "
            "no public URL; the platform is used internally."
        ),
        "results_statement": (
            "Private internal project, in development. No public launch, no "
            "public URL, and no performance, user or revenue metrics are claimed."
        ),
        "technology_stack": "Python, Django, PostgreSQL, HTML, Tailwind CSS, JavaScript",
        "project_duration": "In Development",
        "tags": (
            "Lead Management, Customer Records, Sales Pipeline, Booking "
            "Scheduling, Team Directory, Role-Based Access, Dashboards, "
            "Reporting, Announcements, private-project"
        ),
        "is_featured": True,
        "is_concept_project": True,
        "meta_title": "Custom CRM Software Development Project | GrowthSpare IT Solutions",
        "meta_description": (
            "GrowthSpare Custom CRM is a private internal CRM project covering "
            "lead management, sales pipeline, team workflows, dashboards and "
            "admin controls."
        ),
    },
    # ------------------------------------------------------------------
    # 6. Browser Gaming & Tournament Platform — prototype (NO public URL)
    # ------------------------------------------------------------------
    {
        "slug": "browser-gaming-tournament-platform",
        "title": "Browser Gaming & Tournament Platform",
        "category_slugs": ["gaming", "web-applications"],
        "featured_image": f"{VISUAL_BASE}/browser-gaming-tournament-platform.svg",
        "video_url": None,
        "live_url": None,
        "client_name": "GrowthSpare IT Solutions",
        "industry": "Gaming / Web Application",
        "problem_statement": (
            "GrowthSpare set out to explore a browser-based gaming and "
            "tournament platform: competitive gaming experiences where players "
            "can discover games, keep profiles, join single-player, "
            "multiplayer and tournament play, follow leaderboards and earn "
            "rewards — all launched directly in the browser with no downloads."
        ),
        "solution_statement": (
            "The platform is being designed and built as a browser-based web "
            "application prototype using GrowthSpare's standard web stack. The "
            "intended experience areas are game discovery and launching, player "
            "profiles with login, single-player and multiplayer flows, "
            "tournament workflows, leaderboards, rewards, and custom player "
            "characters. Every listed area is prototype scope under active "
            "development — none of it is described as launched or live."
        ),
        "results_statement": (
            "Prototype, in development. Not publicly launched: no active users, "
            "no running tournaments, and no prizes are being distributed. "
            "Nothing on this page claims a launch, a user base, or live "
            "competition."
        ),
        "technology_stack": "HTML, CSS, JavaScript, Python, Django",
        "project_duration": "Prototype / In Development",
        "tags": (
            "Browser Gaming, Game Launcher, Single Player, Multiplayer, "
            "Tournaments, Player Profiles, Login, Leaderboards, Rewards, "
            "Custom Player Character, prototype"
        ),
        "is_featured": True,
        "is_concept_project": True,
        "meta_title": "Browser Gaming & Tournament Platform | GrowthSpare IT Solutions",
        "meta_description": (
            "A browser gaming and tournament platform prototype by GrowthSpare "
            "IT Solutions covering game discovery, profiles, tournaments and "
            "leaderboards."
        ),
    },
    # ------------------------------------------------------------------
    # 7. Social Media CRM — private internal project (NO public URL)
    # ------------------------------------------------------------------
    # No dedicated Social Media CRM module exists in this repository
    # (verified: no model, migration, view, or history). This entry is
    # therefore scoped STRICTLY to workspace-present capabilities shared
    # with the Custom CRM — it organises enquiries arriving via social,
    # WhatsApp and website channels into one triage pipeline. It claims
    # no platform API sync, no auto-posting, no analytics integrations,
    # no public URL, no users and no metrics.
    # ------------------------------------------------------------------
    {
        "slug": "social-media-crm",
        "title": "Social Media CRM",
        "category_slugs": ["crm-saas-solutions", "digital-marketing"],
        "featured_image": f"{VISUAL_BASE}/social-media-crm.svg",
        "video_url": None,
        "live_url": None,
        "client_name": "GrowthSpare IT Solutions",
        "industry": "Internal Tools / Social CRM",
        "problem_statement": (
            "GrowthSpare receives enquiries from several directions — website "
            "contact forms, consultation bookings, WhatsApp messages and "
            "social profiles such as Instagram. Without one place to triage "
            "them, follow-ups depend on whoever happened to see each message "
            "first."
        ),
        "solution_statement": (
            "The Social Media CRM is being developed as a private internal "
            "workspace on GrowthSpare's standard Django stack that brings "
            "social, WhatsApp and website enquiries into the same pipeline "
            "used by the Custom CRM. It builds only on capabilities already "
            "present in this workspace: enquiry and lead capture with budget "
            "and service routing, a consultation booking pipeline with triage "
            "statuses (pending, scheduled, completed, cancelled), role-based "
            "dashboards showing lead and booking activity with recent items, "
            "a team and client directory with role-based access, and "
            "role-targeted announcements. There is no public URL; the "
            "workspace is used internally while in development."
        ),
        "results_statement": (
            "Private internal project, in development. No public launch, no "
            "public URL, and no performance, user or revenue metrics are claimed."
        ),
        "technology_stack": "Python, Django, PostgreSQL, HTML, Tailwind CSS, JavaScript",
        "project_duration": "In Development",
        "tags": (
            "Social Lead Management, Conversations Inbox, Triage Pipeline, "
            "Lead Management, Booking Scheduling, Team Directory, "
            "Role-Based Access, Dashboards, Announcements, private-project"
        ),
        # Not featured on the homepage rotation (which shows the six
        # established entries) while private/in-development; fully listed
        # in /portfolio/, filters, sitemap and search.
        "is_featured": False,
        "is_concept_project": True,
        "meta_title": "Social Media CRM Software Project | GrowthSpare IT Solutions",
        "meta_description": (
            "Social Media CRM is a private internal project by GrowthSpare IT "
            "Solutions bringing social, WhatsApp and website enquiries into "
            "one triage pipeline with dashboards and role-based access."
        ),
    },
    # ------------------------------------------------------------------
    # 8. World of Fragrance — live perfume & attar business website
    # (verified live 2026-10-06: title "World of Fragrance | Perfumes &
    # Attar in Okhla, Delhi"; WhatsApp ordering and map embeds present
    # in page source)
    # ------------------------------------------------------------------
    {
        "slug": "world-of-fragrance",
        "title": "World of Fragrance",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/world-of-fragrance.svg",
        "video_url": None,
        "live_url": "https://world-of-fragrance.netlify.app/",
        "client_name": "World of Fragrance",
        "industry": "Perfume / Attar Business",
        "problem_statement": (
            "World of Fragrance is a wholesale and retail fragrance business "
            "in Batla House, Okhla, New Delhi, selling Indian attars and "
            "imported perfumes. It needed a premium website that presents its "
            "collections and brand story and lets customers order directly "
            "over WhatsApp."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium fragrance business "
            "website presenting Indian attars, imported perfumes and curated "
            "collections alongside the brand story, with direct WhatsApp "
            "ordering and map-based store location for the Okhla outlet."
        ),
        "results_statement": (
            "Delivered and live: a premium perfume and attar business website "
            "covering collections, brand story and WhatsApp ordering. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Perfume Website, Attar, E-Commerce, Business Website, "
            "WhatsApp Ordering, Okhla"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Perfume & Attar Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "World of Fragrance is a live perfume and attar business website "
            "by GrowthSpare IT Solutions covering collections, brand story "
            "and WhatsApp ordering."
        ),
    },
    # ------------------------------------------------------------------
    # 9. VIP Furniture & Interior — live custom furniture website
    # (verified live 2026-10-06: title "VIP Furniture & Interior |
    # Custom Furniture & Interior Work | Pan India"; Tailwind, gallery
    # and WhatsApp enquiry present in page source)
    # ------------------------------------------------------------------
    {
        "slug": "vip-furniture-interior",
        "title": "VIP Furniture & Interior",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/vip-furniture-interior.svg",
        "video_url": None,
        "live_url": "https://vip-furniture-interio.netlify.app/",
        "client_name": "Suraj Sharma - VIP Furniture & Interior",
        "industry": "Custom Furniture / Interiors",
        "problem_statement": (
            "VIP Furniture & Interior is a custom furniture and interior "
            "contractor serving customers pan India. It needed a premium "
            "business website that presents its modular kitchens, bedroom "
            "interiors, wardrobes, TV units, shop and office interiors, and "
            "converts visitors into project enquiries."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium contractor website "
            "presenting custom furniture and interior service lines — modular "
            "kitchens, bedroom interiors, wardrobes, TV units, shop and "
            "office interiors — with a work gallery and WhatsApp, phone and "
            "form-based enquiry conversion."
        ),
        "results_statement": (
            "Delivered and live: a premium furniture and interior contractor "
            "website covering services, gallery and enquiry conversion. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Furniture Website, Interior Design, Modular Kitchen, Wardrobes, "
            "Custom Furniture, Pan India"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Furniture & Interior Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "VIP Furniture & Interior is a live custom furniture and interior "
            "website by GrowthSpare IT Solutions covering modular kitchens, "
            "wardrobes and enquiry conversion."
        ),
    },
    # ------------------------------------------------------------------
    # 10. GP Beauty Hub — live ladies salon website
    # (verified live 2026-10-06: title "GP Beauty Hub | Ladies Beauty
    # Salon in Madipur, Delhi"; Tailwind, gallery and map embeds
    # present in page source)
    # ------------------------------------------------------------------
    {
        "slug": "gp-beauty-hub",
        "title": "GP Beauty Hub",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/gp-beauty-hub.svg",
        "video_url": None,
        "live_url": "https://gp-buety-hub.netlify.app/",
        "client_name": "GP Beauty Hub",
        "industry": "Ladies Beauty Salon",
        "problem_statement": (
            "GP Beauty Hub is a ladies beauty salon in Madipur, West Delhi, "
            "focused on hair transformation services. It needed a premium "
            "website that presents hair smoothing, keratin, straightening, "
            "hair color, bridal makeup, nail art and mehndi, and converts "
            "visitors into bookings."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium salon website "
            "presenting hair transformation services — smoothing, keratin, "
            "straightening and color — plus bridal makeup, nail art and "
            "mehndi, with a services gallery, map-based salon location and "
            "phone/form booking conversion."
        ),
        "results_statement": (
            "Delivered and live: a premium beauty salon website covering "
            "hair services, bridal and nail art, gallery and booking "
            "conversion. No performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Salon Website, Beauty Salon, Hair Smoothing, Keratin, Bridal "
            "Makeup, Madipur"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Beauty Salon Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "GP Beauty Hub is a live ladies beauty salon website by "
            "GrowthSpare IT Solutions covering hair services, bridal makeup "
            "and booking conversion."
        ),
    },
    # ------------------------------------------------------------------
    # 11. WM Sofa Maker — live sofa manufacturer website
    # (verified live 2026-10-06: title "WM Sofa Maker | Designer &
    # Custom Sofas in Moradabad"; Tailwind, gallery and WhatsApp
    # enquiry present in page source)
    # ------------------------------------------------------------------
    {
        "slug": "wm-sofa-maker",
        "title": "WM Sofa Maker",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/wm-sofa-maker.svg",
        "video_url": None,
        "live_url": "https://wm-sofa-maker.netlify.app/",
        "client_name": "WM Sofa Maker",
        "industry": "Furniture / Sofa Manufacturing",
        "problem_statement": (
            "WM Sofa Maker is a furniture manufacturer in Moradabad, Uttar "
            "Pradesh, building designer and custom sofas. It needed a premium "
            "website that presents its sofa collections and craftsmanship and "
            "converts visitors into customer enquiries."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium manufacturer website "
            "presenting designer sofas and custom sofa solutions with "
            "collections, craftsmanship and gallery sections, plus WhatsApp, "
            "phone and form-based enquiry conversion."
        ),
        "results_statement": (
            "Delivered and live: a premium sofa manufacturer website covering "
            "collections, craftsmanship, gallery and enquiry conversion. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Sofa Manufacturer, Designer Sofas, Custom Sofas, Furniture "
            "Website, Moradabad"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Sofa Manufacturer Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "WM Sofa Maker is a live sofa manufacturer website by GrowthSpare "
            "IT Solutions covering designer sofas, custom builds and enquiry "
            "conversion."
        ),
    },
    # ------------------------------------------------------------------
    # 12. QS Furniture House — live furniture business website
    # (verified live 2026-10-06: title "QS Furniture House | Premium
    # Furniture in Bareilly"; page reachable, HTTP 200)
    # ------------------------------------------------------------------
    {
        "slug": "qs-furniture-house",
        "title": "QS Furniture House",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/qs-furniture-house.svg",
        "video_url": None,
        "live_url": "https://qs-furniture.netlify.app/",
        "client_name": "QS Furniture House",
        "industry": "Furniture / Interiors",
        "problem_statement": (
            "QS Furniture House is a premium furniture business in Bareilly. "
            "It needed a business website that presents its furniture "
            "products and collections and gives customers clear enquiry "
            "options."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium furniture business "
            "website presenting furniture products and collections with "
            "straightforward business enquiry contact options."
        ),
        "results_statement": (
            "Delivered and live: a premium furniture business website "
            "covering products, collections and enquiry options. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Furniture Website, Furniture Business, Collections, Enquiry, "
            "Bareilly"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Furniture Business Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "QS Furniture House is a live furniture business website by "
            "GrowthSpare IT Solutions covering products, collections and "
            "enquiry options."
        ),
    },
    # ------------------------------------------------------------------
    # 13. Five Star Sofa Solution — live sofa & furniture website
    # (verified live 2026-10-06: title "Five Star Sofa Solution |
    # Premium Sofas, Beds & Furniture in Shalimar Garden, Ghaziabad";
    # gallery, WhatsApp and map embeds present in page source)
    # ------------------------------------------------------------------
    {
        "slug": "five-star-sofa-solution",
        "title": "Five Star Sofa Solution",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/five-star-sofa-solution.svg",
        "video_url": None,
        "live_url": "https://five-star-s.netlify.app/",
        "client_name": "Five Star Sofa Solution",
        "industry": "Furniture / Sofas & Beds",
        "problem_statement": (
            "Five Star Sofa Solution is a furniture business in Shalimar "
            "Garden, Ghaziabad, selling sofas, beds and furniture solutions. "
            "It needed a premium website with strong visual product "
            "presentation and an enquiry-focused customer journey."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium furniture website "
            "presenting sofas, beds and furniture solutions with visual "
            "product sections, a gallery and WhatsApp, phone and form-based "
            "enquiry conversion."
        ),
        "results_statement": (
            "Delivered and live: a premium furniture website covering sofas, "
            "beds, product presentation and enquiry conversion. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Sofa Website, Furniture Website, Beds, Product Showcase, "
            "Ghaziabad"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Sofa & Furniture Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "Five Star Sofa Solution is a live furniture website by "
            "GrowthSpare IT Solutions covering sofas, beds and enquiry "
            "conversion."
        ),
    },
    # ------------------------------------------------------------------
    # 14. SM Car Customs — live car modification website
    # (verified live 2026-10-06: title "SM Car Customs | Car
    # Modification & Detailing in Rohini Delhi"; Tailwind, gallery,
    # WhatsApp and map embeds present in page source)
    # ------------------------------------------------------------------
    {
        "slug": "sm-car-customs",
        "title": "SM Car Customs",
        "category_slugs": ["website-development"],
        "featured_image": f"{VISUAL_BASE}/sm-car-customs.svg",
        "video_url": None,
        "live_url": "https://leafy-mochi-527dc3.netlify.app/",
        "client_name": "SM Car Customs",
        "industry": "Automotive / Car Modification",
        "problem_statement": (
            "SM Car Customs is a car modification, customization and "
            "detailing business in Rohini, Delhi. It needed a premium website "
            "with a strong visual identity that presents its services and "
            "converts visitors into enquiries."
        ),
        "solution_statement": (
            "GrowthSpare designed and built a premium automotive website "
            "presenting car modification, customization and detailing services "
            "with a visual gallery, map-based workshop location and WhatsApp, "
            "phone and form-based enquiry conversion."
        ),
        "results_statement": (
            "Delivered and live: a premium automotive website covering "
            "modification services, gallery and enquiry conversion. No "
            "performance metrics are claimed."
        ),
        "technology_stack": "HTML, CSS, Tailwind CSS, JavaScript, Netlify",
        "project_duration": "Delivered",
        "tags": (
            "Automotive Website, Car Modification, Car Detailing, "
            "Customization, Rohini"
        ),
        "is_featured": False,
        "is_concept_project": False,
        "meta_title": "Car Modification Website Project | GrowthSpare IT Solutions",
        "meta_description": (
            "SM Car Customs is a live automotive website by GrowthSpare IT "
            "Solutions covering car modification, detailing and enquiry "
            "conversion."
        ),
    },
]


# ----------------------------------------------------------------------
# Legacy visual repair map: every portfolio slug gets its self-hosted
# project-specific SVG. Applied idempotently to rows seeded earlier by
# seed_database.py (Unsplash hotlinks) or left blank — only the
# featured_image column is touched, and only when it is empty or still
# points at Unsplash. No other field is modified, no rows are created.
# ----------------------------------------------------------------------
LEGACY_VISUAL_REPAIR = {
    "bake-wonders": f"{VISUAL_BASE}/bake-wonders.svg",
    "social-frame-creative": f"{VISUAL_BASE}/social-frame-creative.svg",
    "mac-interio": f"{VISUAL_BASE}/mac-interio.svg",
    "furniture-studio-by-akdas": f"{VISUAL_BASE}/furniture-studio-by-akdas.svg",
    "growthspare-custom-crm": f"{VISUAL_BASE}/growthspare-custom-crm.svg",
    "browser-gaming-tournament-platform": (
        f"{VISUAL_BASE}/browser-gaming-tournament-platform.svg"
    ),
    "social-media-crm": f"{VISUAL_BASE}/social-media-crm.svg",
    "bitecraft-restaurant-website-for-spice-garden": (
        f"{VISUAL_BASE}/bitecraft-restaurant-website-for-spice-garden.svg"
    ),
    "smilecare-professional-dental-clinic-website": (
        f"{VISUAL_BASE}/smilecare-professional-dental-clinic-website.svg"
    ),
    "ironpulse-modern-gym-fitness-website": (
        f"{VISUAL_BASE}/ironpulse-modern-gym-fitness-website.svg"
    ),
    "urbannest-real-estate-agency-website": (
        f"{VISUAL_BASE}/urbannest-real-estate-agency-website.svg"
    ),
    "vibeevents-ticket-booking-event-platform": (
        f"{VISUAL_BASE}/vibeevents-ticket-booking-event-platform.svg"
    ),
    "scholargrid-symmetric-academic-lms-platform": (
        f"{VISUAL_BASE}/scholargrid-symmetric-academic-lms-platform.svg"
    ),
    "grandvista-hotel-reservation-pms-platform": (
        f"{VISUAL_BASE}/grandvista-hotel-reservation-pms-platform.svg"
    ),
    "swiftdrop-logistics-tracking-mobile-app-backend": (
        f"{VISUAL_BASE}/swiftdrop-logistics-tracking-mobile-app-backend.svg"
    ),
    "safeinspected-property-inspection-mobile-compliance": (
        f"{VISUAL_BASE}/safeinspected-property-inspection-mobile-compliance.svg"
    ),
    "indobulk-wholesale-procurement-portal-system": (
        f"{VISUAL_BASE}/indobulk-wholesale-procurement-portal-system.svg"
    ),
    "techvibe-subscription-content-media-publisher": (
        f"{VISUAL_BASE}/techvibe-subscription-content-media-publisher.svg"
    ),
    "whatsapp-lead-collection-bot-for-local-retailer": (
        f"{VISUAL_BASE}/whatsapp-lead-collection-bot-for-local-retailer.svg"
    ),
    "ai-customer-support-chatbot-for-e-commerce": (
        f"{VISUAL_BASE}/ai-customer-support-chatbot-for-e-commerce.svg"
    ),
    "brightacademy-school-management-crm": (
        f"{VISUAL_BASE}/brightacademy-school-management-crm.svg"
    ),
    "salesflow-b2b-lead-management-crm": (
        f"{VISUAL_BASE}/salesflow-b2b-lead-management-crm.svg"
    ),
    "social-media-growth-campaign-for-local-cafe": (
        f"{VISUAL_BASE}/social-media-growth-campaign-for-local-cafe.svg"
    ),
    "local-seo-optimization-for-dental-clinic": (
        f"{VISUAL_BASE}/local-seo-optimization-for-dental-clinic.svg"
    ),
    "elevate-workforce-international-recruitment-job-board-platform": (
        f"{VISUAL_BASE}/elevate-workforce-international-recruitment-job-board-platform.svg"
    ),
    "heartland-hills-farm-farm-land-showcase-site-visit-landing-site": (
        f"{VISUAL_BASE}/heartland-hills-farm-farm-land-showcase-site-visit-landing-site.svg"
    ),
}


class Command(BaseCommand):
    help = "Seeds the genuine GrowthSpare portfolio projects (idempotent)."

    def handle(self, *args, **options):
        _get_or_create_category("Website Development", "website-development")
        _get_or_create_category("CRM & SaaS Solutions", "crm-saas-solutions")
        _get_or_create_category("Digital Marketing", "digital-marketing")
        _get_or_create_category("Gaming", "gaming")
        _get_or_create_category("Web Applications", "web-applications")

        for entry in PROJECTS:
            data = dict(entry)
            slug = data.pop("slug")
            category_slugs = data.pop("category_slugs")
            project, created = Project.objects.update_or_create(
                slug=slug, defaults=data
            )
            project.categories.set(
                ProjectCategory.objects.filter(slug__in=category_slugs)
            )
            action = "Created" if created else "Updated"
            self.stdout.write(
                f"{action}: {project.title} "
                f"[{project.display_status_label}] "
                f"live_url={project.live_url or 'NONE'}"
            )

        repaired = 0
        for slug, visual_url in LEGACY_VISUAL_REPAIR.items():
            project = Project.objects.filter(slug=slug).first()
            if project is None:
                continue
            current = (project.featured_image or "").strip()
            if not current or "images.unsplash.com" in current:
                project.featured_image = visual_url
                project.save(update_fields=["featured_image", "updated_at"])
                repaired += 1
        self.stdout.write(f"Repaired legacy visuals: {repaired}")

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Featured projects: "
                f"{Project.objects.filter(is_featured=True).count()}"
            )
        )
