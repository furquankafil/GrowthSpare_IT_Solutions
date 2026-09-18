"""
Class-based views managing portfolio gallery listings, dynamic category
filtering, and detailed project case study rendering.

Updated to correctly prefetch and filter many-to-many categories.
"""

from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
from django.conf import settings
from django.urls import reverse
from .models import Project, ProjectCategory


class PortfolioListView(ListView):
    """
    Renders an interactive catalog of enterprise case studies. Supports dynamic
    filtering of completed systems based on category slugs passed via GET parameters.
    """
    model = Project
    template_name = "portfolio/portfolio_list.html"
    context_object_name = "projects"
    paginate_by = 9

    def get_queryset(self):
        """
        Filters case studies based on category parameter dynamically.
        Uses prefetch_related for many-to-many categories instead of select_related.
        """
        queryset = Project.objects.all().prefetch_related("categories")
        category_slug = self.request.GET.get("category")
        if category_slug:
            # Query against many-to-many relationship using correct field prefix
            queryset = queryset.filter(categories__slug=category_slug).distinct()
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Load all classification parameters to power category selectors on front-end
        context["categories"] = ProjectCategory.objects.all()
        context["active_category"] = self.request.GET.get("category", "")
        # Filtered category views are useful for users but should not be indexed
        # as separate pages (duplicate of the unfiltered portfolio index).
        if self.request.GET.get("category"):
            context["seo_robots"] = "noindex, follow"
        
        # SEO attributes
        context["seo_title"] = "Portfolio & Case Studies"
        context["seo_description"] = (
            "Website, CRM, AI automation and SEO projects by GrowthSpare IT Solutions "
            "for restaurants, clinics, real estate and local businesses."
        )
        base_url = settings.SITE_URL.rstrip("/")
        context["schema_data"] = [
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Portfolio", "item": f"{base_url}{reverse('portfolio:list')}"},
                ],
            }
        ]
        return context


class ProjectDetailView(DetailView):
    """
    Renders comprehensive problem-solving profiles. Fetches supplementary image
    galleries and related completed projects using optimized relational lookups.
    """
    model = Project
    template_name = "portfolio/project_detail.html"
    context_object_name = "project"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        """Optimize data retrieval by prefetching related images and categories."""
        return Project.objects.all().prefetch_related("gallery_images", "categories")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # Fetch up to 3 similar case studies sharing any of this project's categories
        context["related_projects"] = (
            Project.objects.filter(categories__in=project.categories.all())
            .exclude(id=project.id)
            .prefetch_related("categories")
            .distinct()[:3]
        )

        # Forward internal links to genuinely related service pages. The
        # approved service->portfolio relationships live in
        # SERVICE_CONTEXTUAL_LINKS (apps/services/views.py); inverting that
        # map here reuses exactly those relationships in the reverse
        # direction — no new/invented associations, no model changes. Each
        # candidate is verified against an active Service row so the link
        # can never 404.
        context["related_services"] = []
        try:
            from apps.services.views import SERVICE_CONTEXTUAL_LINKS
            from apps.services.models import Service as ServiceModel

            for service_slug, links in SERVICE_CONTEXTUAL_LINKS.items():
                for link in links:
                    if link.get("url_name") != "portfolio:detail":
                        continue
                    if (link.get("kwargs") or {}).get("slug") != project.slug:
                        continue
                    service = ServiceModel.objects.filter(
                        slug=service_slug, is_active=True
                    ).first()
                    if service is not None and all(
                        s["url"] != service.get_absolute_url()
                        for s in context["related_services"]
                    ):
                        context["related_services"].append(
                            {
                                "label": service.title,
                                "url": service.get_absolute_url(),
                            }
                        )
                    break
        except Exception:
            context["related_services"] = []

        # SEO configurations
        context["seo_title"] = (
            project.meta_title
            if project.meta_title
            else f"{project.title} - {'Concept Project' if project.is_concept_project else 'Client Case Study'} ({project.client_name})"
        )
        # Seed data shipped placeholder meta_descriptions like "for X for Y"
        # (see seed_database.py). Treat those (and any <70-char stub) as missing
        # so searchers see a real summary instead of a broken fragment.
        _meta = (project.meta_description or "").strip()
        _is_placeholder = (
            not _meta or len(_meta) < 70 or _meta.lower().startswith("for ")
        )
        if not _is_placeholder:
            context["seo_description"] = _meta
        elif project.is_concept_project:
            context["seo_description"] = (
                f"A concept project illustrating how GrowthSpare IT Solutions would "
                f"approach a {project.industry} engagement like {project.client_name}. "
                f"See the engineering approach and technology stack used."
            )
        else:
            context["seo_description"] = (
                f"Read the success story for {project.client_name}. Learn about the "
                f"engineering challenges faced, our architectural actions, and the "
                f"metrics achieved."
            )

        # Dynamic Schema JSON-LD structure mapping
        # Safely extract first category name if available for JSON-LD data
        first_cat = project.categories.first()
        context["schema_type"] = "CreativeWork"
        creative_work_schema = {
            "@type": "CreativeWork",
            "name": project.title,
            "description": project.problem_statement[:150] + "...",
            "category": first_cat.name if first_cat else "General",
            "creator": {
                "@type": "Organization",
                "@id": f"{settings.SITE_URL.rstrip('/')}/#organization",
                "name": "GrowthSpare IT Solutions",
                "url": settings.SITE_URL,
            },
        }
        # Only attribute a named client relationship in structured data for
        # verified, non-concept engagements — attaching a fabricated
        # Organization name to a concept project here would be a false
        # business-relationship claim indexed directly by search engines.
        if not project.is_concept_project:
            creative_work_schema["client"] = {
                "@type": "Organization",
                "name": project.client_name,
                "industry": project.industry,
            }
        else:
            creative_work_schema["genre"] = "Concept Project"
        base_url = settings.SITE_URL.rstrip("/")
        breadcrumb_schema = {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                {"@type": "ListItem", "position": 2, "name": "Portfolio", "item": f"{base_url}{reverse('portfolio:list')}"},
                {"@type": "ListItem", "position": 3, "name": project.title, "item": f"{base_url}{project.get_absolute_url()}"},
            ],
        }
        context["schema_data"] = [creative_work_schema, breadcrumb_schema]
        return context