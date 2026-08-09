"""
Class-based views managing portfolio gallery listings, dynamic category
filtering, and detailed project case study rendering.

Updated to correctly prefetch and filter many-to-many categories.
"""

from django.views.generic import ListView, DetailView
from django.db.models import Prefetch
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
        
        # SEO attributes
        context["seo_title"] = "Portfolio & Case Studies"
        context["seo_description"] = (
            "Explore our portfolio of website, CRM, AI automation, and SEO "
            "projects. See how GrowthSpare IT Solutions structures robust cloud "
            "databases, deploys AI automation hooks, and implements "
            "high-performance web products."
        )
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

        # SEO configurations
        context["seo_title"] = (
            project.meta_title
            if project.meta_title
            else f"{project.title} - {'Concept Project' if project.is_concept_project else 'Client Case Study'} ({project.client_name})"
        )
        if project.meta_description:
            context["seo_description"] = project.meta_description
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
        context["schema_data"] = {
            "name": project.title,
            "description": project.problem_statement[:150] + "...",
            "category": first_cat.name if first_cat else "General",
            "creator": {
                "@type": "LocalBusiness",
                "name": "GrowthSpare IT Solutions",
            },
        }
        # Only attribute a named client relationship in structured data for
        # verified, non-concept engagements — attaching a fabricated
        # Organization name to a concept project here would be a false
        # business-relationship claim indexed directly by search engines.
        if not project.is_concept_project:
            context["schema_data"]["client"] = {
                "@type": "Organization",
                "name": project.client_name,
                "industry": project.industry,
            }
        else:
            context["schema_data"]["genre"] = "Concept Project"
        return context