"""
Administrative control panel configurations for managing consultation bookings,
scheduling statuses, and Zoom/Google Meet dynamic conference links.
"""

from django.contrib import admin
from .models import ConsultationBooking


@admin.register(ConsultationBooking)
class ConsultationBookingAdmin(admin.ModelAdmin):
    """
    Control room interface managing active scoping requests, allocating scheduled meeting slots,
    binding virtual conference coordinates, and tracking CRM pipeline progression.
    """
    list_display = (
        "name",
        "company",
        "services_required",
        "budget",
        "status",
        "scheduled_time",
        "created_at",
    )
    list_filter = ("status", "services_required", "budget", "created_at")
    search_fields = ("name", "email", "phone", "company", "industry", "project_details", "meeting_link")
    readonly_fields = ("created_at",)
    
    actions = ["mark_as_scheduled", "mark_as_completed", "mark_as_cancelled"]
    
    fieldsets = (
        (
            "Prospect Profile & Enterprise Scope",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "company",
                    "industry",
                )
            },
        ),
        (
            "Project Specifications",
            {
                "fields": (
                    "services_required",
                    "budget",
                    "project_details",
                    "created_at",
                )
            },
        ),
        (
            "Scheduling & Pipeline Coordination",
            {
                "description": "Configure the active schedule status. Assign meeting times and add Zoom/Google Meet links to synchronize calendars.",
                "fields": (
                    "status",
                    "preferred_contact_time",
                    "scheduled_time",
                    "meeting_link",
                ),
            },
        ),
    )

    def mark_as_scheduled(self, request, queryset):
        """Action method to transition bookings to SCHEDULED status in bulk."""
        updated = queryset.update(status="SCHEDULED")
        self.message_user(request, f"Successfully marked {updated} bookings as Scheduled.")
    mark_as_scheduled.short_description = "Mark selected bookings as Scheduled"

    def mark_as_completed(self, request, queryset):
        """Action method to transition bookings to COMPLETED status in bulk."""
        updated = queryset.update(status="COMPLETED")
        self.message_user(request, f"Successfully marked {updated} bookings as Completed.")
    mark_as_completed.short_description = "Mark selected bookings as Completed"

    def mark_as_cancelled(self, request, queryset):
        """Action method to transition bookings to CANCELLED status in bulk."""
        updated = queryset.update(status="CANCELLED")
        self.message_user(request, f"Successfully marked {updated} bookings as Cancelled.")
    mark_as_cancelled.short_description = "Mark selected bookings as Cancelled"