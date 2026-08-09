from django.shortcuts import render

# Create your views here.
"""
Class-based views managing global customer review lists and enterprise social proof feeds.
"""

from django.views.generic import ListView
from .models import Testimonial


class TestimonialListView(ListView):
    """
    Renders the client reviews directory. Loads and displays active
    customer endorsements alongside their respective designations and corporate contexts.
    Note: seeded testimonials are clearly labelled "Sample Review" in the
    template until replaced with genuine, verified client feedback.
    """
    model = Testimonial
    template_name = "testimonials/testimonial_list.html"
    context_object_name = "testimonials"
    paginate_by = 12

    def get_queryset(self):
        """Retrieves and displays active customer reviews safely."""
        return Testimonial.objects.filter(is_active=True).select_related("project")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Custom SEO attributes
        context["seo_title"] = "Client Reviews & Testimonials"
        context["seo_description"] = (
            "Read client feedback for GrowthSpare IT Solutions, covering website "
            "development, AI automation, CRM, and SEO projects."
        )
        return context