"""
URL configuration for GrowthSpare IT Solutions project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/stable/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ADD THESE TWO IMPORTS
from django.views.generic import RedirectView
from django.templatetags.static import static as static_file

# Global exception handlers pointing to custom views inside core application
handler404 = "apps.core.views.custom_handler_404"
handler500 = "apps.core.views.custom_handler_500"

urlpatterns = [
    # Root favicon (https://growthspareitsolutions.com/favicon.ico)
    path(
        "favicon.ico",
        RedirectView.as_view(
            url=static_file("images/favicon.ico"),
            permanent=True,
        ),
    ),

    # Enterprise Admin Command Console
    path("admin/", admin.site.urls),

    # Custom Identity and Workspace Access App
    path("accounts/", include("apps.accounts.urls", namespace="accounts")),

    # Internal Dashboard Workspace App
    path("dashboard/", include("apps.dashboard.urls", namespace="dashboard")),

    # Services Catalog & Capabilities Modules
    path("services/", include("apps.services.urls", namespace="services")),

    # Case Studies and Project Galleries App
    path("portfolio/", include("apps.portfolio.urls", namespace="portfolio")),

    # Dynamic Editorial & Marketing Insights App
    path("blog/", include("apps.blog.urls", namespace="blog")),

    # Contact Communications Portal App
    path("contact/", include("apps.contact.urls", namespace="contact")),

    # Consultation Multi-Step System App
    path("consultation/", include("apps.consultation.urls", namespace="consultation")),

    # Dynamic FAQ Accordion Management App
    path("faq/", include("apps.faq.urls", namespace="faq")),

    # Client Testimonials Management App
    path("testimonials/", include("apps.testimonials.urls", namespace="testimonials")),

    # Core Landing, Informational Views & Global Operations Router
    path("", include("apps.core.urls", namespace="core")),
]

# Static & Media Asset Routing constraints during local development cycles
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)