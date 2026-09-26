"""
Seeds the six genuine GrowthSpare portfolio projects.

Idempotent: safe to re-run (upserts by slug, resets category links).

Honesty rules enforced here (see PORTFOLIO_IMPLEMENTATION_REPORT.md):
- The four live sites were verified against their live HTML on 2026-09-26
  (content sections) and their HTML source (technology stack). Only
  verified facts are stored — no metrics, reviews, ratings or awards.
- The CRM entry has NO public URL and only lists capabilities already
  present in this workspace (contact lead capture, consultation pipeline
  with triage statuses, role-based dashboards, team directory, role
  announcements). It is tagged "private-project".
- The gaming entry has NO public URL and every listed area is framed as
  intended prototype scope, never as launched. Tagged "prototype".
- featured_image is intentionally left empty: with no permission to reuse
  the businesses' photography, cards render an honest CSS monogram
  placeholder instead of a fake screenshot.
"""

from django.core.management.base import BaseCommand

from apps.portfolio.models import Project, ProjectCategory


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
        "featured_image": "",
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
        "featured_image": "",
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
        "featured_image": "",
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
        "featured_image": "",
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
        "featured_image": "",
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
        "featured_image": "",
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
]


class Command(BaseCommand):
    help = "Seeds the six genuine GrowthSpare portfolio projects (idempotent)."

    def handle(self, *args, **options):
        _get_or_create_category("Website Development", "website-development")
        _get_or_create_category("CRM & SaaS Solutions", "crm-saas-solutions")
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

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Featured projects: "
                f"{Project.objects.filter(is_featured=True).count()}"
            )
        )
