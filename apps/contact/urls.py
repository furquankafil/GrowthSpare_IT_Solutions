"""
URL configurations mapping general B2B contact pages and post ingestion endpoints
to class-based views.
"""

from django.urls import path
from . import views

app_name = "contact"

urlpatterns = [
    # General Corporate Contact Page & Form Handler
    path("", views.ContactView.as_view(), name="contact"),
]