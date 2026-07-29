"""
Administrative dashboard configurations for global platform FAQs,
mapping sort priority categories and active status switches.
"""

from django.contrib import admin
from .models import FAQCategory, FAQItem


class FAQItemInline(admin.TabularInline):
    """Enables additions of FAQ items directly within the dynamic topic category view."""
    model = FAQItem
    extra = 2
    classes = ("collapse",)
    ordering = ("order",)


@admin.register(FAQCategory)
class FAQCategoryAdmin(admin.ModelAdmin):
    """Admin configuration managing global categorization topics."""
    inlines = [FAQItemInline]
    prepopulated_fields = {"slug": ("name",)}
    list_display = ("name", "order", "slug")
    list_editable = ("order",)
    search_fields = ("name",)


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    """Admin configuration managing individual answers inside dynamic accordion pools."""
    list_display = ("question", "category", "order", "is_active")
    list_filter = ("category", "is_active")
    list_editable = ("order", "is_active")
    search_fields = ("question", "answer")
    
    fieldsets = (
        (
            "FAQ Item Structure",
            {
                "fields": (
                    "category",
                    "question",
                    "answer",
                    "order",
                    "is_active",
                )
            },
        ),
    )