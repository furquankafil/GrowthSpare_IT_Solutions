"""
Administrative dashboard configurations for corporate solutions and services management,
enabling horizontal pick lists for multi-category selections and inline FAQ updates.
"""

from django.contrib import admin
from .models import Service, ServiceCategory, ServiceFAQ


class ServiceFAQInline(admin.TabularInline):
    """Enables seamless additions of service-level FAQs within the same administrative view."""
    model = ServiceFAQ
    extra = 1
    classes = ("collapse",)  # Keeps layout compact unless administrative view requires edit
    fields = ("question", "answer", "order")
    ordering = ("order",)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    """Admin configuration for service group classifications and order priorities."""
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "order", "slug")
    list_editable = ("order",)
    search_fields = ("name",)


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """
    Control room interface managing active system capabilities, dynamic pricing indicators,
    and associated SEO parameters.
    
    Updated to support safe multi-category selections horizontally.
    """
    inlines = [ServiceFAQInline]
    prepopulated_fields = {"slug": ("title",)}
    filter_horizontal = ("categories",)  # Enables clean multi-category pick lists
    
    list_display = (
        "title",
        "pricing_estimate",
        "get_categories",  # Custom helper displaying mapped classifications cleanly
        "is_active",
        "updated_at",
    )
    list_filter = ("is_active", "categories")
    search_fields = ("title", "overview", "detailed_description", "technologies")
    
    fieldsets = (
        (
            "Core Identity",
            {
                "fields": (
                    "title",
                    "slug",
                    "icon_class",
                    "categories",
                    "is_active",
                )
            },
        ),
        (
            "Service Overview & Description",
            {
                "fields": (
                    "overview",
                    "detailed_description",
                )
            },
        ),
        (
            "Structured Components",
            {
                "description": "Lists structured for layout splitting inside details pages. Features/Benefits/Process/Use Cases/Why Choose Us are line-split.",
                "fields": (
                    "features",
                    "benefits",
                    "process_steps",
                    "use_cases",
                    "why_choose_us",
                    "technologies",
                    "pricing_estimate",
                ),
            },
        ),
        (
            "Call-To-Action Banner",
            {
                "description": "Optional custom copy for this service's detail-page CTA banner. Falls back to generic copy if left blank.",
                "fields": (
                    "cta_headline",
                    "cta_subtext",
                ),
            },
        ),
        (
            "Hardened Search Optimization (SEO)",
            {
                "classes": ("collapse",),
                "fields": (
                    "meta_title",
                    "meta_description",
                ),
            },
        ),
    )

    def get_categories(self, obj):
        """Compiles associated categories into a comma-separated list for index views."""
        return ", ".join([c.name for c in obj.categories.all()])
    get_categories.short_description = "Assigned Categories"