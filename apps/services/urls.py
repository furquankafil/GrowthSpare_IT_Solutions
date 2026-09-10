"""
URL configurations mapping lists of capability solutions and structural details pages
to custom class-based controllers.
"""

from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "services"

urlpatterns = [
    # Services Catalog Main Index
    path("", views.ServiceListView.as_view(), name="list"),

    # Dedicated Category Landing Pages (e.g. /services/category/web-solutions/)
    # Kept under a "category/" prefix so a category slug can never collide
    # with an individual Service's own detail slug below.
    path("category/<slug:category_slug>/", views.ServiceCategoryView.as_view(), name="category"),

    # Short commercial aliases (stakeholder-requested clean URLs) — 301 to
    # canonical DB-backed detail pages. No duplicate content: these never render,
    # they only redirect. Must sit ABOVE the generic <slug:slug> pattern.
    path("web-development/", RedirectView.as_view(pattern_name="services:detail", permanent=True, query_string=False), {"slug": "website-development"}),
    path("web-design/", RedirectView.as_view(pattern_name="services:detail", permanent=True, query_string=False), {"slug": "website-development"}),
    path("seo/", RedirectView.as_view(pattern_name="services:detail", permanent=True, query_string=False), {"slug": "seo-optimization"}),
    path("ai-development/", RedirectView.as_view(pattern_name="services:detail", permanent=True, query_string=False), {"slug": "ai-whatsapp-automation"}),

    # Custom Dynamic Service Detail Page
    path("<slug:slug>/", views.ServiceDetailView.as_view(), name="detail"),
]