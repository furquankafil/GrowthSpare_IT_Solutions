"""
URL configurations mapping informational landing points, legal compliance grids,
async subscriber handshakes, and dynamically generated sitemaps / robots configurations.
"""

from django.urls import path
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import (
    StaticViewSitemap,
    BlogSitemap,
    ServiceSitemap,
    ServiceCategorySitemap,
    PortfolioSitemap,
)

app_name = "core"

# Dictionary of active dynamic index maps used by search engine crawlers
sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "service-categories": ServiceCategorySitemap,
    "portfolio": PortfolioSitemap,
    "blogs": BlogSitemap,
}

urlpatterns = [
    # Container / load-balancer health probe (Docker HEALTHCHECK, Nginx, Render, Railway, Cloud Run)
    path("ping", views.health_check, name="ping"),

    # General Corporate Pages
    path("", views.HomeView.as_view(), name="home"),
    path("about-us/", views.AboutView.as_view(), name="about"),

    # Local SEO — City Landing Pages (Delhi HQ + wider NCR)
    path("locations/web-development-delhi/", views.LocationLandingView.as_view(), {"location_slug": "delhi"}, name="location-delhi"),
    path("locations/web-development-noida/", views.LocationLandingView.as_view(), {"location_slug": "noida"}, name="location-noida"),
    path("locations/web-development-gurgaon/", views.LocationLandingView.as_view(), {"location_slug": "gurgaon"}, name="location-gurgaon"),

    # Industry-Specific Landing Pages
    path("industries/restaurant-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "restaurant-website-development"}, name="industry-restaurant"),
    path("industries/real-estate-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "real-estate-website-development"}, name="industry-real-estate"),
    path("industries/clinic-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "clinic-website-development"}, name="industry-clinic"),
    path("industries/education-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "education-website-development"}, name="industry-education"),
    path("industries/small-business-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "small-business-website-development"}, name="industry-small-business"),
    path("industries/gym-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "gym-website-development"}, name="industry-gym-fitness"),
    path("industries/law-firm-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "law-firm-website-development"}, name="industry-law-firm"),
    path("industries/ecommerce-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "ecommerce-website-development"}, name="industry-retail-ecommerce"),
    path("industries/corporate-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "corporate-website-development"}, name="industry-corporate-business"),
    path("industries/hotel-travel-website-development/", views.IndustryLandingView.as_view(), {"industry_slug": "hotel-travel-website-development"}, name="industry-hotels-travel"),

    # Legal and SLA Compliance Pages
    path("privacy-policy/", views.PrivacyPolicyView.as_view(), name="privacy"),
    path("terms-and-conditions/", views.TermsView.as_view(), name="terms"),
    path("refund-policy/", views.RefundPolicyView.as_view(), name="refund"),
    path("cookies-policy/", views.CookiesPolicyView.as_view(), name="cookies"),
    
    # Asynchronous Engagement Actions
    path("newsletter/subscribe/", views.NewsletterSubscribeView.as_view(), name="newsletter_subscribe"),

    # Direct Search Engine Optimization Crawling Tunnels
    path(
        "robots.txt",
        TemplateView.as_view(template_name="core/robots.txt", content_type="text/plain"),
        name="robots",
    ),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
]