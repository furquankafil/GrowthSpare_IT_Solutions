"""
URL configurations mapping informational landing points, legal compliance grids,
async subscriber handshakes, and dynamically generated sitemaps / robots configurations.
"""

from django.urls import path
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap

from . import views
from .sitemaps import StaticViewSitemap, BlogSitemap, ServiceSitemap, PortfolioSitemap

app_name = "core"

# Dictionary of active dynamic index maps used by search engine crawlers
sitemaps = {
    "static": StaticViewSitemap,
    "services": ServiceSitemap,
    "portfolio": PortfolioSitemap,
    "blogs": BlogSitemap,
}

urlpatterns = [
    # Container / load-balancer health probe (Docker HEALTHCHECK, Nginx, Render, Railway, Cloud Run)
    path("ping", views.health_check, name="ping"),

    # General Corporate Pages
    path("", views.HomeView.as_view(), name="home"),
    path("about-us/", views.AboutView.as_view(), name="about"),
    
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