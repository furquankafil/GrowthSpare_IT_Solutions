"""
Core page routing views, corporate compliance pages, async newsletter subscription endpoints,
and secure dynamic 404/500 exception handling views.
"""

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.http import JsonResponse, Http404
from django_ratelimit.decorators import ratelimit

from .models import NewsletterSubscriber, ClientLogo
from apps.services.models import Service
from apps.portfolio.models import Project
from apps.blog.models import BlogPost
from apps.testimonials.models import Testimonial


# ==============================================================================
# Homepage FAQ (AEO) — single source of truth.
# These are the exact, visible Q&A pairs rendered in the homepage accordion and
# mirrored 1:1 into FAQPage structured data. Answers are concise and factual,
# based only on documented service capabilities / existing site content.
# ==============================================================================
HOMEPAGE_FAQS = [
    (
        "What services does GrowthSpare IT Solutions provide?",
        "We provide website development, AI & WhatsApp automation, custom CRM "
        "software, SaaS and custom software engineering, SEO & digital marketing, "
        "and cyber security services for startups, small businesses, and growing companies.",
    ),
    (
        "How much does a business website cost?",
        "Our standard business websites start at ₹4,999. Final pricing depends on "
        "the number of pages, features, and content readiness. Share your "
        "requirements and we'll quote accurately.",
    ),
    (
        "How long does website development take?",
        "Most standard business websites are delivered in 2-4 weeks, depending on "
        "the number of pages and how quickly content is provided. Larger web "
        "applications and SaaS builds take longer and are scoped individually.",
    ),
    (
        "Do you provide website development in Delhi?",
        "Yes. We are based in Okhla, New Delhi, and build websites for businesses "
        "across Delhi — with in-person meetings available when a project needs them.",
    ),
    (
        "Do you serve businesses in Noida and Gurugram?",
        "Yes. We work with businesses in Noida and Gurugram as well as Delhi, "
        "covering the wider NCR region. Projects can be delivered fully remotely "
        "or with in-person meetings.",
    ),
    (
        "Can you build custom CRM software?",
        "Yes. We build custom CRM systems tailored to your sales process — leads, "
        "customers, invoicing, and team permissions — which you own outright, "
        "with no per-seat subscription fees.",
    ),
    (
        "Can you automate business processes using AI?",
        "Yes. We build AI and WhatsApp automations for lead collection, appointment "
        "booking, and customer support, built on the official WhatsApp Cloud API "
        "and OpenAI models, with human handoff built in.",
    ),
    (
        "Do you provide SEO services?",
        "Yes. We provide technical, on-page, and local SEO services to help your "
        "business rank higher on Google and grow organic traffic sustainably.",
    ),
    (
        "How long does SEO take?",
        "SEO is a compounding channel. Most businesses start seeing meaningful "
        "movement in 3-6 months, with continued growth after that. We focus on "
        "sustainable white-hat practices and don't guarantee specific rankings.",
    ),
    (
        "Do you provide website maintenance?",
        "Yes. We offer maintenance and support plans that keep your website "
        "updated, secure, and running smoothly — including backups, security "
        "patches, and monitoring.",
    ),
]


# sameAs entries are ONLY the profiles already linked in the public footer
# (LinkedIn company page, Instagram, Facebook). Nothing invented.
COMPANY_SAME_AS = [
    "https://www.linkedin.com/company/growthspareitsolution/",
    "https://www.instagram.com/growthspareitsolution/",
    "https://www.facebook.com/profile.php?id=61592462990102",
]


def _company_local_business_schema():
    """Shared NAP + hours entity block reused by LocalBusiness schemas."""
    return {
        "@type": "LocalBusiness",
        "name": "GrowthSpare IT Solutions",
        "url": settings.SITE_URL,
        "logo": f"{settings.SITE_URL}/static/images/logo.png",
        "image": f"{settings.SITE_URL}/static/images/logo.png",
        "description": "Website development, AI automation, CRM software, SEO & digital marketing for startups and SMEs in Delhi NCR.",
        "email": "growthspareitsolution@gmail.com",
        "telephone": "+91 9811579273",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": "D-50, Shaheen Bagh, Okhla",
            "addressLocality": "New Delhi",
            "postalCode": "110025",
            "addressCountry": "IN",
        },
        # Business hours already stated on the public contact page.
        "openingHoursSpecification": {
            "@type": "OpeningHoursSpecification",
            "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
            "opens": "09:00",
            "closes": "19:00",
        },
        "sameAs": COMPANY_SAME_AS,
    }


class HomeView(TemplateView):
    """
    Renders the premium corporate landing engine. Passes dynamic structural parameters
    including latest portfolio highlights, active service capabilities, and recent blog entries.
    """
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load active business solutions, newest case studies, and editorial articles
        context["featured_services"] = Service.objects.filter(is_active=True).order_by("id")
        context["featured_projects"] = Project.objects.filter(is_featured=True)[:3]
        context["recent_blogs"] = BlogPost.objects.filter(is_published=True).order_by("-published_at")[:3]
        context["testimonials"] = Testimonial.objects.filter(is_active=True).select_related("project")[:6]

        # Client/partner logos for the "Trusted by" strip. Each entry renders
        # its uploaded logo image, or falls back to an initials badge in the
        # template when no logo file has been uploaded for that client.
        context["client_logos"] = ClientLogo.objects.filter(is_active=True)

        # Homepage FAQ (AEO): visible accordion content + matching FAQPage schema.
        context["homepage_faqs"] = HOMEPAGE_FAQS

        # Structured data: LocalBusiness entity + FAQPage, emitted as one @graph
        # (a single script tag per page, which is what Google's tooling expects).
        local_business_schema = _company_local_business_schema()
        local_business_schema["@id"] = f"{settings.SITE_URL}/#organization"
        local_business_schema["areaServed"] = ["New Delhi", "Noida", "Gurugram"]
        faq_schema = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in HOMEPAGE_FAQS
            ],
        }
        context["schema_data"] = [local_business_schema, faq_schema]

        # SEO parameters
        context["seo_title"] = "Web Development, AI & CRM in Delhi NCR"
        context["seo_description"] = (
            "Website development, AI automation, CRM software, SEO & digital "
            "marketing for startups & SMEs in Delhi, Noida & Gurugram. Based in New Delhi."
        )
        return context


class AboutView(TemplateView):
    """Renders our company story, leadership matrices, values, and global delivery standards."""
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Our Vision & Enterprise Engineering Leadership"
        context["seo_description"] = "Learn how GrowthSpare IT Solutions helps businesses scale globally using advanced technology."
        return context


# ==============================================================================
# Local SEO — City Landing Pages
# ==============================================================================
# GrowthSpare is based in Delhi and actively serves the wider NCR region. Each
# entry below is written with genuinely distinct, non-interchangeable content
# per city (not the same paragraph with the city name swapped) so these don't
# read as thin doorway pages. One TemplateView + one shared template handles
# all of them, matching the existing pattern used by ServiceCategoryView, so
# no new app/model/duplicate templates were needed for this.
LOCATION_DATA = {
    "delhi": {
        "city": "Delhi",
        "seo_title": "Web Development & IT Services in Delhi",
        "seo_description": "GrowthSpare IT Solutions is based in Delhi, offering website development, AI automation, and digital marketing to local businesses across the capital.",
        "heading": "Web Development & IT Services in Delhi",
        "intro": (
            "GrowthSpare IT Solutions is headquartered in Okhla, Delhi, and works "
            "directly with businesses across the capital — from established retail "
            "and trading businesses in Old Delhi and Karol Bagh, to service "
            "businesses and startups in South and Central Delhi."
        ),
        "context_paragraphs": [
            "Delhi's business landscape is unusually varied — wholesale and retail traders, "
            "clinics and educational institutes, hospitality businesses, and a growing base "
            "of small consulting and service firms all operate side by side. A website or "
            "digital presence that works for a boutique consultancy rarely works the same "
            "way for a wholesale trading business, so we scope each Delhi project around "
            "the specific way that business actually gets customers today — WhatsApp "
            "enquiries, walk-ins, referrals, or Google search — rather than a one-size-fits-all template.",
            "Being based in Delhi ourselves means in-person meetings are straightforward "
            "when a project needs them, and there's no timezone or working-hours friction "
            "in day-to-day communication during the build.",
        ],
        "services_focus": [
            "Business & E-commerce Websites",
            "Local SEO & Google Business Profile Optimization",
            "WhatsApp Lead Automation for Retail & Service Businesses",
            "Custom CRM for Trading & Distribution Businesses",
        ],
        "faqs": [
            ("Are you actually based in Delhi, or is this just a landing page?", "Yes, our office is in Okhla, New Delhi. In-person meetings are available for Delhi-based clients when a project calls for it."),
            ("Do you work with wholesale/trading businesses, not just tech startups?", "Yes — a meaningful share of our Delhi client base is retail, wholesale, and trading businesses that need a straightforward web presence or a WhatsApp/CRM system, not a complex tech product."),
            ("How much does a business website cost in Delhi?", "It depends on scope, but our standard business websites start at ₹4,999. Get in touch with your requirements and we'll quote accurately."),
        ],
    },
    "noida": {
        "city": "Noida",
        "seo_title": "Web Development & IT Services in Noida",
        "seo_description": "IT services for Noida-based startups, IT/ITES companies, and small businesses — website development, AI automation, and CRM from GrowthSpare IT Solutions.",
        "heading": "Web Development & IT Services in Noida",
        "intro": (
            "Noida is one of the NCR's larger IT and startup corridors, home to everything "
            "from early-stage startups working out of coworking spaces in Sector 62 and "
            "Sector 16 to established IT/ITES companies along the Noida Expressway. "
            "GrowthSpare works with Noida-based businesses that need a technically solid "
            "web presence or internal tooling, not just a template site."
        ),
        "context_paragraphs": [
            "Because a large share of Noida's business base is itself tech-literate — "
            "founders and teams who've worked in software before — the bar for what counts "
            "as a 'good' website or internal tool tends to be higher than in a purely "
            "non-technical market. We lean into that: clean code, real performance "
            "budgets, and systems built to be handed off or extended by an in-house team later if needed.",
            "Noida's proximity to Delhi means the same in-person availability applies here "
            "too — client meetings, discovery calls, or a site visit are all straightforward to arrange.",
        ],
        "services_focus": [
            "Startup & SaaS Product Websites",
            "Custom CRM & Internal Tooling for IT/ITES Companies",
            "AI & WhatsApp Automation",
            "Technical SEO for Product-Led Businesses",
        ],
        "faqs": [
            ("Do you work with early-stage startups on a limited budget?", "Yes, we scope projects to match early-stage budgets and can phase a build so core functionality ships first."),
            ("Can you build internal tools/dashboards, not just a public website?", "Yes — custom internal tooling and dashboards for operations, reporting, or CRM are a regular part of our Noida client work."),
            ("Do you provide ongoing technical support after launch?", "Yes, we offer maintenance and support plans, which matter more for Noida clients running active SaaS products or internal systems."),
        ],
    },
    "gurgaon": {
        "city": "Gurugram (Gurgaon)",
        "seo_title": "Web Development & IT Services in Gurugram (Gurgaon)",
        "seo_description": "IT services for Gurugram-based corporates, consultancies, and D2C brands — website development, CRM, and digital marketing from GrowthSpare IT Solutions.",
        "heading": "Web Development & IT Services in Gurugram (Gurgaon)",
        "intro": (
            "Gurugram is home to a dense concentration of corporate offices, consulting "
            "firms, fintech and real estate businesses, and D2C brands, particularly along "
            "Cyber City, MG Road, and Golf Course Road. GrowthSpare works with Gurugram "
            "businesses that need a polished, professional web presence to match "
            "corporate-facing or investor-facing standards."
        ),
        "context_paragraphs": [
            "A lot of Gurugram's business activity is B2B or investor-facing rather than "
            "purely consumer-facing, which changes what a website actually needs to do — "
            "credibility and clarity of positioning often matter more than volume of "
            "traffic. We build accordingly: clean corporate design, clear service/offering "
            "structure, and lead-capture built around consultations rather than impulse purchases.",
            "For D2C and real estate businesses specifically — both common in this market — "
            "we also focus on fast page loads and mobile experience, since that's where "
            "most of that traffic actually comes from.",
        ],
        "services_focus": [
            "Corporate & Consulting Firm Websites",
            "Real Estate & D2C Brand Websites",
            "CRM Systems for B2B Sales Teams",
            "SEO for Competitive, High-Value Keywords",
        ],
        "faqs": [
            ("Do you work with corporate/B2B clients, or mainly small local businesses?", "Both — our Gurugram client base leans more corporate and B2B than our Delhi base, and we scope projects (positioning, structure, lead capture) accordingly."),
            ("Can you build a real estate microsite or listing platform?", "Yes, real estate microsites and listing-driven websites are one of our regular project types."),
            ("Do you provide CRM systems for B2B sales pipelines specifically?", "Yes, we build custom CRM systems shaped around a specific sales process, which is common for B2B teams in Gurugram."),
        ],
    },
}


class LocationLandingView(TemplateView):
    """
    Renders a single city's local SEO landing page from LOCATION_DATA above.
    One shared template + one dict of real, hand-written content per city —
    deliberately not a database-backed app, since 3 hand-curated pages don't
    warrant a new model/migration/admin surface.
    """
    template_name = "core/location_landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        location = LOCATION_DATA.get(kwargs["location_slug"])
        if location is None:
            raise Http404("Unknown location.")
        context["location"] = location
        context["seo_title"] = location["seo_title"]
        context["seo_description"] = location["seo_description"]

        # LocalBusiness (scoped to this city) + FAQPage schema, combined —
        # matches the pattern used on service detail pages.
        local_business_schema = {
            "@type": "LocalBusiness",
            "name": "GrowthSpare IT Solutions",
            "url": settings.SITE_URL,
            "telephone": "+91 9811579273",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "D-50, Shaheen Bagh, Okhla",
                "addressLocality": "New Delhi",
                "postalCode": "110025",
                "addressCountry": "IN",
            },
            "areaServed": location["city"],
        }
        faq_schema = {
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": question,
                    "acceptedAnswer": {"@type": "Answer", "text": answer},
                }
                for question, answer in location["faqs"]
            ],
        }
        context["schema_data"] = [local_business_schema, faq_schema]
        return context


# ==============================================================================
# Industry-Specific Landing Pages
# ==============================================================================
INDUSTRY_DATA = {
    "restaurant-website-development": {
        "name": "Restaurant Website Development",
        "seo_title": "Restaurant Website Development Services",
        "seo_description": "Websites for restaurants and cafes — menu display, table reservations, and online ordering integration, built by GrowthSpare IT Solutions.",
        "heading": "Restaurant Website Development",
        "problem": (
            "Most restaurants either have no website at all, or rely entirely on a "
            "third-party listing (Zomato/Swiggy) for their online presence — which means "
            "they don't own the relationship with a customer who found them online, and "
            "pay a commission on every order routed that way."
        ),
        "solution": (
            "We build fast, mobile-first restaurant websites that display your menu clearly, "
            "let customers reserve a table or contact you directly on WhatsApp, and reduce "
            "your dependency on third-party platforms for direct/repeat customers."
        ),
        "features": [
            "Mobile-optimized digital menu with categories and pricing",
            "Table reservation form with WhatsApp confirmation",
            "Google Maps + Google Business Profile integration for 'near me' visibility",
            "Photo gallery for ambience, dishes, and events",
        ],
        "faqs": [
            ("Can you integrate online ordering?", "Yes, we can integrate WhatsApp-based ordering directly, or link out to your existing Zomato/Swiggy listings if you want to keep using them alongside your own site."),
            ("Do you handle the menu photography too?", "We can advise on menu photography, but photography/shoot production itself isn't part of our standard scope — we focus on the website and digital presence."),
        ],
    },
    "real-estate-website-development": {
        "name": "Real Estate Website Development",
        "seo_title": "Real Estate Website Development Services",
        "seo_description": "Property listing websites and real estate microsites with lead capture, built by GrowthSpare IT Solutions.",
        "heading": "Real Estate Website Development",
        "problem": (
            "Real estate buyers and investors research extensively online before ever "
            "contacting an agent or developer. A weak or slow property website loses "
            "serious buyers before they even reach out."
        ),
        "solution": (
            "We build property listing websites and project microsites with fast image-heavy "
            "page performance, clear property/unit information, and lead-capture forms "
            "designed to convert a browsing visitor into an enquiry."
        ),
        "features": [
            "Property/unit listing pages with filterable details",
            "Lead capture forms routed to WhatsApp/email/CRM",
            "Image galleries and virtual tour embed support",
            "Fast page loads even with high-resolution property photography",
        ],
        "faqs": [
            ("Can you build a microsite for a single project/development?", "Yes — single-project real estate microsites (for one building/development rather than a full listings platform) are one of our regular project types."),
            ("Can leads flow directly into a CRM?", "Yes, we can connect the lead form to our custom CRM system or an existing tool you use."),
        ],
    },
    "clinic-website-development": {
        "name": "Clinic & Healthcare Website Development",
        "seo_title": "Clinic & Healthcare Website Development Services",
        "seo_description": "Websites for clinics, dentists, and healthcare practices — appointment booking, service listings, and local SEO from GrowthSpare IT Solutions.",
        "heading": "Clinic & Healthcare Website Development",
        "problem": (
            "Patients increasingly search for a clinic or doctor online before booking, "
            "and expect to see clear service information, credentials, and an easy way "
            "to book an appointment — not just a phone number on a business card."
        ),
        "solution": (
            "We build clean, trustworthy clinic websites with clear service listings, "
            "doctor/staff profiles, and an appointment request flow, optimized to rank "
            "for local 'near me' healthcare searches."
        ),
        "features": [
            "Appointment booking / request form with WhatsApp confirmation",
            "Service and specialization listing pages",
            "Doctor/staff profile pages",
            "Local SEO structured for 'near me' healthcare searches",
        ],
        "faqs": [
            ("Can the website handle appointment scheduling directly?", "Yes, we can build an appointment request flow. For complex multi-doctor scheduling with real-time calendar sync, we'll scope that as a slightly larger custom build."),
            ("Do you follow any specific healthcare compliance standards?", "We build with standard web security best practices (HTTPS, secure forms, rate limiting). For specific regulatory compliance requirements, let us know upfront so we can scope accordingly."),
        ],
    },
    "education-website-development": {
        "name": "Education & Coaching Website Development",
        "seo_title": "Education & Coaching Institute Website Development",
        "seo_description": "Websites for schools, coaching institutes, and online course providers, built by GrowthSpare IT Solutions.",
        "heading": "Education & Coaching Website Development",
        "problem": (
            "Parents and students research a school or coaching institute's reputation, "
            "faculty, and results online before enrolling — an outdated or missing website "
            "actively costs enrollments to competitors with a stronger digital presence."
        ),
        "solution": (
            "We build education websites covering course/program listings, faculty "
            "profiles, admission enquiry forms, and — where relevant — a simple student "
            "portal or LMS integration."
        ),
        "features": [
            "Course/program listing pages",
            "Admission enquiry form with WhatsApp/email routing",
            "Faculty and facility showcase pages",
            "Optional LMS/student portal integration for online course providers",
        ],
        "faqs": [
            ("Can you build a full LMS, not just a marketing website?", "Yes, we've built LMS-style platforms as custom software projects. For a marketing website with admission enquiries, that's covered under standard website development."),
            ("Do you handle multi-branch/multi-location coaching institutes?", "Yes, we can structure the site with location-specific pages for each branch."),
        ],
    },
    "small-business-website-development": {
        "name": "Small Business Website Development",
        "seo_title": "Small Business Website Development Services",
        "seo_description": "Affordable, professional websites for small businesses — retail, services, and local shops — from GrowthSpare IT Solutions.",
        "heading": "Small Business Website Development",
        "problem": (
            "Many small businesses either have no website, or one that was built years "
            "ago and never updated — meaning they're effectively invisible to customers "
            "searching online today."
        ),
        "solution": (
            "We build straightforward, professional small business websites — a clear "
            "explanation of what you offer, how to reach you, and a way to capture leads "
            "via WhatsApp or a contact form — without unnecessary complexity or cost."
        ),
        "features": [
            "Clear service/product presentation",
            "WhatsApp and contact form lead capture built in",
            "Google Business Profile alignment for local search",
            "Fast, mobile-first design",
        ],
        "faqs": [
            ("I don't have any existing branding or content — can you still help?", "Yes, we can work with minimal starting material and guide you through what's needed (logo, photos, service descriptions) as part of the project."),
            ("What's the starting price for a small business website?", "Our standard business websites start at ₹4,999 — get in touch with your specific requirements for an accurate quote."),
        ],
    },
}


class IndustryLandingView(TemplateView):
    """
    Renders a single industry's landing page from INDUSTRY_DATA above.
    Same lightweight pattern as LocationLandingView — one shared template,
    hand-written genuinely distinct content per industry, no new app/model.
    """
    template_name = "core/industry_landing.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        industry = INDUSTRY_DATA.get(kwargs["industry_slug"])
        if industry is None:
            raise Http404("Unknown industry.")
        context["industry"] = industry
        context["seo_title"] = industry["seo_title"]
        context["seo_description"] = industry["seo_description"]

        if industry.get("faqs"):
            context["schema_type"] = "FAQPage"
            context["schema_data"] = {
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": question,
                        "acceptedAnswer": {"@type": "Answer", "text": answer},
                    }
                    for question, answer in industry["faqs"]
                ]
            }
        return context


class PrivacyPolicyView(TemplateView):
    """Corporate data security compliance page detailing handling under standard ISO protocols."""
    template_name = "core/privacy.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Privacy Policy"
        context["seo_description"] = "Read the GrowthSpare IT Solutions data protection parameters, compliance protocols, and strict user security rules."
        return context


class TermsView(TemplateView):
    """Legal service level agreements and structural user operation terms."""
    template_name = "core/terms.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Terms of Service"
        context["seo_description"] = "Review the official Terms of Service and Service Level Agreements governing GrowthSpare IT Solutions technology deployments and platforms."
        return context


class RefundPolicyView(TemplateView):
    """Standard SLA billing, retainer timelines, and service cancellation matrices."""
    template_name = "core/refund.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Billing & Refund Policy"
        context["seo_description"] = "Review the billing, cancellation, milestone validation, and refund terms of service for software development and AI integration services."
        return context


class CookiesPolicyView(TemplateView):
    """Detailed analytics collection, persistent cookie usage, and privacy controls."""
    template_name = "core/cookies.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Cookie Policy"
        context["seo_description"] = "Read the official Cookie Policy for GrowthSpare IT Solutions. Learn how we use persistent browser storage to improve site performance."
        return context


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class NewsletterSubscribeView(View):
    """
    Asynchronous JSON-ready subscription endpoint processing incoming marketing 
    subscription requests and logging validation records in the subscriber model.
    Rate-limited to 5 POSTs/minute per IP.
    """

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip().lower()
        if not email:
            return JsonResponse({"success": False, "message": "Email field is required."})

        # Model.save() does not run field validators — validate explicitly
        # before writing, otherwise malformed strings land straight in the DB.
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "message": "Please provide a valid email address."})

        # Process subscriber save pipeline safely
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created:
            if subscriber.is_active:
                return JsonResponse({"success": True, "message": "You are already active in our newsletter loop."})
            else:
                subscriber.is_active = True
                subscriber.save()
                return JsonResponse({"success": True, "message": "Your newsletter subscription has been reactivated!"})

        return JsonResponse({"success": True, "message": "Successfully subscribed to GrowthSpare IT Solutions bulletins!"})


# ==============================================================================
# Security Exceptions & Client Failure Handlers (CBV & standard mapping)
# ==============================================================================

def health_check(request):
    """
    Lightweight liveness/readiness endpoint for Docker HEALTHCHECK, Nginx,
    and cloud platform health probes (Render, Railway, Cloud Run). Intentionally
    avoids heavy DB/cache calls so it responds fast under load.
    """
    return JsonResponse({"status": "ok"})


def custom_handler_404(request, exception=None):
    """Renders highly polished corporate 404 template with helpful navigation nodes."""
    response = render(request, "core/404.html", status=404)
    return response


def custom_handler_500(request):
    """Renders static corporate 500 failure state when internal code boundaries fail."""
    response = render(request, "core/500.html", status=500)
    return response