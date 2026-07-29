"""
Dynamic XML sitemap definitions for search engine bots, indexing core pages,
operational services, case studies, and corporate publications.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.services.models import Service
from apps.portfolio.models import Project
from apps.blog.models import BlogPost


class StaticViewSitemap(Sitemap):
    """Generates the main index map for core structural pages."""
    priority = 0.8
    changefreq = "weekly"

    def items(self):
        return [
            "core:home",
            "core:about",
            "core:privacy",
            "core:terms",
            "core:refund",
            "core:cookies",
            "contact:contact",
            "consultation:book",
        ]

    def location(self, item):
        return reverse(item)


class ServiceSitemap(Sitemap):
    """Maps dynamic service detail records for search discovery optimization."""
    priority = 0.9
    changefreq = "monthly"

    def items(self):
        # Only query active corporate solutions
        return Service.objects.filter(is_active=True)

    def lastmod(self, obj):
        # Fallback timestamp handling if database model track flags change
        return obj.updated_at


class PortfolioSitemap(Sitemap):
    """Maps custom development case studies, aligning outcomes and problems."""
    priority = 0.7
    changefreq = "monthly"

    def items(self):
        return Project.objects.all()

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    """Maps published corporate editorial and growth insights."""
    priority = 0.6
    changefreq = "daily"

    def items(self):
        return BlogPost.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at