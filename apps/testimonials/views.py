from django.shortcuts import render

# Create your views here.
"""
Class-based views managing global customer review lists and enterprise social proof feeds.
"""

from django.views.generic import ListView
from .models import Testimonial


class TestimonialListView(ListView):
    """
    Renders the verified corporate reviews directory. Loads and displays active
    customer endorsements alongside their respective designations and corporate contexts.
    """
    model = Testimonial
    template_name = "testimonials/testimonial_list.html"
    context_object_name = "testimonials"
    paginate_by = 12

    def get_queryset(self):
        """Retrieves and displays verified corporate reviews safely."""
        return Testimonial.objects.filter(is_active=True).select_related("project")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Custom SEO attributes
        context["seo_title"] = "Verified Corporate Testimonials & Case Study Success Reviews"
        context["seo_description"] = (
            "Explore reviews and ratings from our B2B partners, company founders, "
            "and directors globally detailing their technology optimization outcomes with "
            "GrowthSpare IT Solutions."
        )
        return context