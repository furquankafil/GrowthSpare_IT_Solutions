"""
Class-based views managing capability catalog indexing, dynamic category pre-fetches,
and high-performance, SEO-optimized detailed capability page renderings.

Serves all 7 active service divisions: Web Solutions, AI Automation, SaaS & CRM
Systems, Digital Marketing, SEO & Marketing, Cyber Security, and Engineering Solutions.
"""

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import ListView, DetailView
from .models import Service, ServiceCategory


# Services whose delivery genuinely targets the Delhi NCR market. Only these
# carry an `areaServed` in their Service schema — the rest are delivered
# remotely nationwide and don't over-claim a location.
LOCAL_SERVICE_SLUGS = {
    "website-development",
    "digital-marketing",
    "seo-optimization",
}

# Per-service contextual internal links to pages that already exist on the
# site (location, industry, and portfolio URLs). Natural, varied anchor text —
# nothing invented, nothing pointing at a non-existent URL.
SERVICE_CONTEXTUAL_LINKS = {
    "website-development": [
        {"label": "web development services in Delhi", "url_name": "core:location-delhi"},
        {"label": "web development in Noida", "url_name": "core:location-noida"},
        {"label": "web development in Gurugram", "url_name": "core:location-gurgaon"},
        {"label": "restaurant website development", "url_name": "core:industry-restaurant"},
        {"label": "clinic website development", "url_name": "core:industry-clinic"},
        {"label": "small business website development", "url_name": "core:industry-small-business"},
        {"label": "real estate website development", "url_name": "core:industry-real-estate"},
        {"label": "education website development", "url_name": "core:industry-education"},
        {"label": "restaurant website project for Spice Garden", "url_name": "portfolio:detail", "kwargs": {"slug": "bitecraft-restaurant-website-for-spice-garden"}},
    ],
    "digital-marketing": [
        {"label": "social media growth campaign for a local café", "url_name": "portfolio:detail", "kwargs": {"slug": "social-media-growth-campaign-for-local-cafe"}},
    ],
    "seo-optimization": [
        {"label": "local SEO optimization for a dental clinic", "url_name": "portfolio:detail", "kwargs": {"slug": "local-seo-optimization-for-dental-clinic"}},
    ],
    "ai-whatsapp-automation": [
        {"label": "AI customer support chatbot for e-commerce", "url_name": "portfolio:detail", "kwargs": {"slug": "ai-customer-support-chatbot-for-e-commerce"}},
        {"label": "WhatsApp lead collection bot for a local retailer", "url_name": "portfolio:detail", "kwargs": {"slug": "whatsapp-lead-collection-bot-for-local-retailer"}},
    ],
    "crm-software-development": [
        {"label": "SalesFlow B2B lead management CRM", "url_name": "portfolio:detail", "kwargs": {"slug": "salesflow-b2b-lead-management-crm"}},
        {"label": "BrightAcademy school management CRM", "url_name": "portfolio:detail", "kwargs": {"slug": "brightacademy-school-management-crm"}},
    ],
    "custom-software-engineering": [
        {"label": "ScholarGrid academic LMS platform", "url_name": "portfolio:detail", "kwargs": {"slug": "scholargrid-symmetric-academic-lms-platform"}},
        {"label": "TechVibe subscription content publisher", "url_name": "portfolio:detail", "kwargs": {"slug": "techvibe-subscription-content-media-publisher"}},
    ],
}


class ServiceListView(ListView):
    """
    Renders a comprehensive corporate solutions index catalog. Displays
    active system capabilities and B2B solutions, prefetching related
    many-to-many categories to prevent query duplication bottlenecks.

    Also supports an optional `?category=<slug>` query parameter (used by
    older/bookmarked links) to narrow the catalog down to a single
    category without a full page redirect. The canonical, crawlable way to
    browse a single category is the dedicated `services:category` URL
    (e.g. /services/category/web-solutions/), handled by ServiceCategoryView
    below.
    """
    model = Service
    template_name = "services/service_list.html"
    context_object_name = "services"

    def get_queryset(self):
        """
        Filter capabilities to active service provisions and prefetch categories.
        Narrows further to a single category when `?category=<slug>` is present.
        """
        queryset = Service.objects.filter(is_active=True).prefetch_related("categories")

        category_slug = self.request.GET.get("category")
        if category_slug:
            queryset = queryset.filter(categories__slug=category_slug)

        # distinct() is required once we join across the M2M "categories"
        # table, otherwise services mapped to >1 matching category would
        # be duplicated in the results.
        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["categories"] = ServiceCategory.objects.all().order_by("order")

        category_slug = self.request.GET.get("category")
        context["active_category"] = (
            context["categories"].filter(slug=category_slug).first() if category_slug else None
        )

        # Custom SEO attributes for the overall catalog view
        if context["active_category"]:
            context["seo_title"] = f"{context['active_category'].name} Services"
            context["seo_description"] = (
                f"Explore our {context['active_category'].name} solutions, engineered to help "
                f"modern businesses automate workflows and scale faster."
            )
        else:
            context["seo_title"] = "Web, AI, SaaS, Security & Engineering Solutions"
            context["seo_description"] = (
                "Explore our complete directory of business-first services: Web Solutions, AI "
                "Automation, SaaS & CRM Systems, Digital Marketing, SEO & Marketing, Cyber Security, "
                "and Engineering Solutions."
            )

        # Real category-based groupings for the two "Division" sections on the
        # unfiltered /services/ page (previously matched on hardcoded title
        # substrings such as "Digital" or "SEO", which had nothing to do with
        # the actual Service<->ServiceCategory relationship).
        base_queryset = self.get_queryset()
        context["growth_marketing_services"] = base_queryset.filter(
            categories__slug__in=["digital-marketing", "seo-marketing"]
        ).distinct()
        context["technology_services"] = base_queryset.exclude(
            categories__slug__in=["digital-marketing", "seo-marketing"]
        ).distinct()
        return context


class ServiceCategoryView(ListView):
    """
    Renders the dedicated, crawlable category landing page (e.g.
    /services/category/web-solutions/), showing ONLY the active services
    mapped to that single ServiceCategory via the Service<->ServiceCategory
    many-to-many relationship.
    """
    model = Service
    template_name = "services/category.html"
    context_object_name = "services"

    def get_category(self):
        """Resolve the ServiceCategory once per request, 404 on an unknown slug."""
        if not hasattr(self, "_category"):
            category_slug = self.kwargs["category_slug"]
            self._category = get_object_or_404(ServiceCategory, slug=category_slug)
        return self._category

    def get_queryset(self):
        category = self.get_category()
        return (
            Service.objects.filter(is_active=True, categories=category)
            .prefetch_related("categories")
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category = self.get_category()
        context["category"] = category
        context["category_name"] = category.name
        context["categories"] = ServiceCategory.objects.all().order_by("order")

        context["seo_title"] = f"{category.name} Services"
        context["seo_description"] = (
            f"Explore our high-performance suite of {category.name} services, engineered to "
            f"help modern businesses automate workflows and scale faster."
        )
        return context


class ServiceDetailView(DetailView):
    """
    Constructs high-converting unique capability detail pages. Pre-loads line-split
    data arrays, many-to-many categories, and related ServiceFAQs using optimized prefetch limits.
    """
    model = Service
    template_name = "services/service_detail.html"
    context_object_name = "service"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Optimize data retrieval by prefetching related FAQs and categories."""
        return Service.objects.filter(is_active=True).prefetch_related("service_faqs", "categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        service = self.object

        categories = list(service.categories.all())

        # Retrieve up to 3 similar services sharing any of this service's categories
        context["related_services"] = (
            Service.objects.filter(categories__in=categories, is_active=True)
            .exclude(id=service.id)
            .prefetch_related("categories")
            .distinct()[:3]
        )

        # Resolve custom SEO configurations or fallback dynamically
        context["seo_title"] = service.meta_title if service.meta_title else f"{service.title} Services"
        context["seo_description"] = (
            service.meta_description
            if service.meta_description
            else f"Explore our high-performance {service.title} solutions. Learn about features, benefits, processes, and tech stacks."
        )

        # Contextual internal links to real location/industry/portfolio pages
        # (see SERVICE_CONTEXTUAL_LINKS). Resolved here so the template never
        # has to reason about url_name/kwargs.
        context["service_links"] = []
        for link in SERVICE_CONTEXTUAL_LINKS.get(service.slug, []):
            context["service_links"].append(
                {
                    "label": link["label"],
                    "url": reverse(link["url_name"], kwargs=link.get("kwargs") or {}),
                }
            )

        # Visible breadcrumb trail: Home > Services > Category > Service
        context["breadcrumb_category"] = categories[0] if categories else None

        # Build schema data structure dynamically to render in JSON-LD headers.
        # Combined as a single @graph: Service schema plus BreadcrumbList, plus
        # FAQPage schema when this service actually has active FAQs (matches
        # what's visibly on the page — FAQPage schema on a page without visible
        # qualifying FAQs violates Google's structured data guidelines).
        service_schema = {
            "name": service.title,
            "description": service.overview,
            "url": f"{settings.SITE_URL}{service.get_absolute_url()}",
            "provider": {
                "@type": "LocalBusiness",
                "name": "GrowthSpare IT Solutions",
                "url": settings.SITE_URL,
            },
            "offers": {
                "@type": "Offer",
                "priceCurrency": "INR",
                "description": service.pricing_estimate,
            },
        }
        if service.slug in LOCAL_SERVICE_SLUGS:
            service_schema["areaServed"] = ["New Delhi", "Noida", "Gurugram"]
        service_schema["@type"] = "Service"

        base_url = settings.SITE_URL.rstrip("/")
        breadcrumb_items = [
            {"name": "Home", "url": f"{base_url}/"},
            {"name": "Services", "url": f"{base_url}{reverse('services:list')}"},
        ]
        if categories:
            breadcrumb_items.append(
                {
                    "name": categories[0].name,
                    "url": f"{base_url}{reverse('services:category', kwargs={'category_slug': categories[0].slug})}",
                }
            )
        breadcrumb_items.append({"name": service.title, "url": f"{base_url}{service.get_absolute_url()}"})
        breadcrumb_schema = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": position,
                    "name": item["name"],
                    "item": item["url"],
                }
                for position, item in enumerate(breadcrumb_items, start=1)
            ],
        }

        schema_blocks = [service_schema, breadcrumb_schema]

        active_faqs = list(service.service_faqs.all())
        if active_faqs:
            faq_schema = {
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": faq.question,
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": faq.answer,
                        },
                    }
                    for faq in active_faqs
                ],
            }
            schema_blocks.append(faq_schema)

        context["schema_data"] = schema_blocks
        return context