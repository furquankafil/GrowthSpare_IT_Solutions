"""
Class-based views managing capability catalog indexing, dynamic category pre-fetches,
and high-performance, SEO-optimized detailed capability page renderings.

Serves all 7 active service divisions: Web Solutions, AI Automations, SaaS & CRM
Systems, Digital Growth, SEO & Marketing, Cyber Security, and Engineering Solutions.
"""

from django.shortcuts import get_object_or_404
from django.views.generic import ListView, DetailView
from .models import Service, ServiceCategory


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
                "Automations, SaaS & CRM Systems, Digital Growth, SEO & Marketing, Cyber Security, "
                "and Engineering Solutions."
            )

        # Real category-based groupings for the two "Division" sections on the
        # unfiltered /services/ page (previously matched on hardcoded title
        # substrings such as "Digital" or "SEO", which had nothing to do with
        # the actual Service<->ServiceCategory relationship).
        base_queryset = self.get_queryset()
        context["growth_marketing_services"] = base_queryset.filter(
            categories__slug__in=["digital-growth", "seo-marketing"]
        ).distinct()
        context["technology_services"] = base_queryset.exclude(
            categories__slug__in=["digital-growth", "seo-marketing"]
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

        # Retrieve up to 3 similar services sharing any of this service's categories
        context["related_services"] = (
            Service.objects.filter(categories__in=service.categories.all(), is_active=True)
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

        # Build schema data structure dynamically to render in JSON-LD headers
        context["schema_type"] = "Service"
        context["schema_data"] = {
            "name": service.title,
            "description": service.overview,
            "provider": {
                "@type": "LocalBusiness",
                "name": "GrowthSpare IT Solutions",
                "url": "https://growthspareitsolutions.com",
            },
            "offers": {
                "@type": "Offer",
                "priceCurrency": "INR",
                "description": service.pricing_estimate,
            },
        }
        return context