"""AppConfig definition for the consultation application."""

from django.apps import AppConfig


class ConsultationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.consultation"
    verbose_name = "Scoping & Consultation Funnel"