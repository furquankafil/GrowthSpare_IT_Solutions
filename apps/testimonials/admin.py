"""
Administrative configurations for client testimonials management,
supporting sorting ordering and active display flags.
"""

from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    """
    Control room interface managing corporate reviews, star scale weights,
    and associated customer avatar assets.
    """
    list_display = (
        "client_name",
        "company_name",
        "designation",
        "rating",
        "is_active",
        "order",
        "created_at",
    )
    list_filter = ("rating", "is_active", "created_at")
    list_editable = ("is_active", "order")
    search_fields = ("client_name", "company_name", "designation", "review")
    
    fieldsets = (
        (
            "Reviewer Profile Details",
            {
                "fields": (
                    "client_name",
                    "company_name",
                    "designation",
                    "client_avatar",
                )
            },
        ),
        (
            "Corporate Statement Data",
            {
                "fields": (
                    "review",
                    "rating",
                    "project",
                )
            },
        ),
        (
            "Visual Sorting Controls",
            {
                "fields": (
                    "is_active",
                    "order",
                )
            },
        ),
    )