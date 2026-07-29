from django.shortcuts import render

# Create your views here.
"""
Class-based views managing global FAQ accordion lists and optimized category pre-fetches.
"""

from django.db import models
from django.views.generic import ListView
from .models import FAQCategory, FAQItem


class FAQListView(ListView):
    """
    Renders the dynamic corporate knowledge base index. Group FAQ accordions
    hierarchically under their parent categories utilizing optimized Prefetch boundaries.
    """
    model = FAQCategory
    template_name = "faq/faq_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        """Loads and pre-filters active FAQ items under structural categories safely."""
        # Use Prefetch queries to optimize dynamic inner queries and prevent N+1 queries in loop
        active_faqs_prefetch = models.Prefetch(
            "faqs",
            queryset=FAQItem.objects.filter(is_active=True),
            to_attr="active_faqs"
        )
        return FAQCategory.objects.all().prefetch_related(active_faqs_prefetch)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Custom SEO attributes
        context["seo_title"] = "Dynamic FAQs & Knowledge Base Directory"
        context["seo_description"] = (
            "Explore answers to frequently asked technical and process questions regarding "
            "AI Automation, custom Django platforms, SaaS integrations, and search engine optimization "
            "delivery parameters structured by GrowthSpare IT Solutions."
        )
        return context