"""
Administrative control panel configurations for managing incoming client leads,
general inquiries, and process states inside pipeline systems.
"""

from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Control room interface managing active system leads, reviewing client budgets,
    service interests, and logging custom processing notes.
    """
    list_display = (
        "name",
        "email",
        "phone",
        "company",
        "service",
        "budget",
        "is_processed",
        "created_at",
    )
    list_filter = ("is_processed", "service", "budget", "created_at")
    search_fields = ("name", "email", "phone", "company", "message", "admin_notes")
    readonly_fields = ("created_at",)
    
    actions = ["mark_as_processed", "mark_as_unprocessed"]
    
    fieldsets = (
        (
            "Client Profile & Coordinates",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "company",
                )
            },
        ),
        (
            "Lead Scope Details",
            {
                "fields": (
                    "service",
                    "budget",
                    "message",
                    "created_at",
                )
            },
        ),
        (
            "Internal Process Controls",
            {
                "fields": (
                    "is_processed",
                    "admin_notes",
                )
            },
        ),
    )

    def mark_as_processed(self, request, queryset):
        """Action method to flag leads as processed in bulk."""
        updated = queryset.update(is_processed=True)
        self.message_user(request, f"Successfully flagged {updated} inquiries as processed.")
    mark_as_processed.short_description = "Mark selected inquiries as processed"

    def mark_as_unprocessed(self, request, queryset):
        """Action method to flag leads as unprocessed/pending in bulk."""
        updated = queryset.update(is_processed=False)
        self.message_user(request, f"Successfully flagged {updated} inquiries as pending/unprocessed.")
    mark_as_unprocessed.short_description = "Mark selected inquiries as pending"