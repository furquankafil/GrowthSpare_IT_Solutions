"""
URL configurations mapping dynamic general FAQ pages and categorized knowledge base grids
to custom views.
"""

from django.urls import path
from . import views

app_name = "faq"

urlpatterns = [
    # General Dynamic FAQ Accordion Feed Page
    path("", views.FAQListView.as_view(), name="list"),
]