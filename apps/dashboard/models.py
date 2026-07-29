"""
Database models representing workspace configurations, system-wide announcements,
and administrative broadcast messages rendered on client and team dashboards.
"""

from django.db import models
from django.conf import settings


class SystemAnnouncement(models.Model):
    """
    Saves and structures operational broadcasts and notices targeted dynamically
    at specific user roles (e.g., Enterprise Clients, Software Engineers) in their workspace panels.
    """
    ROLE_TARGETS = (
        ("ALL", "All Workspace Users"),
        ("CLIENT", "Enterprise Clients Only"),
        ("DEVELOPER", "Software Engineers Only"),
        ("MANAGER", "Project Managers Only"),
        ("ADMIN", "Administrators Only"),
    )

    title = models.CharField(
        max_length=150,
        help_text="Primary broadcast headline statement.",
    )
    content = models.TextField(
        max_length=2000,
        help_text="Detailed broadcast parameters or update message.",
    )
    target_role = models.CharField(
        max_length=20,
        choices=ROLE_TARGETS,
        default="ALL",
        help_text="Filters target audience permission levels.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls visibility thresholds on dashboard landing layouts.",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="announcements",
        help_text="The administrator who generated this announcement.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Workspace Announcement"
        verbose_name_plural = "Workspace Announcements"
        ordering = ["-created_at"]

    def __str__(self):
        return f"[{self.get_target_role_display()}] - {self.title[:40]}..."