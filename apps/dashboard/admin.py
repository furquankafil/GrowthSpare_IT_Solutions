"""
Administrative configurations for system announcements and broadcasts
rendered on customer and manager dashboards.
"""

from django.contrib import admin
from .models import SystemAnnouncement


@admin.register(SystemAnnouncement)
class SystemAnnouncementAdmin(admin.ModelAdmin):
    """
    Control room interface managing workspace bulletins, targeting broadcasts,
    and monitoring active notice states.
    """
    list_display = (
        "title",
        "target_role",
        "is_active",
        "created_by",
        "created_at",
    )
    list_filter = ("target_role", "is_active", "created_at")
    list_editable = ("is_active",)
    search_fields = ("title", "content")
    
    fieldsets = (
        (
            "Broadcast Identity",
            {
                "fields": (
                    "title",
                    "content",
                )
            },
        ),
        (
            "Audience Targeting & State",
            {
                "fields": (
                    "target_role",
                    "is_active",
                    "created_by",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        """Automatically assigns the current user as the author of the bulletin."""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)