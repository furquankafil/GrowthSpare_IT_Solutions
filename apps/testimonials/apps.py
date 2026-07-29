"""AppConfig definition for the testimonials application."""

from django.apps import AppConfig


class TestimonialsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.testimonials"
    verbose_name = "Client Reviews & Social Proof"