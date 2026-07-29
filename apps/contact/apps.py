"""AppConfig definition for the contact application."""

from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.contact"
    verbose_name = "Client Inquiries & Lead Capture"