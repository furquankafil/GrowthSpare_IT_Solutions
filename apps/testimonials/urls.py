"""
URL configurations mapping dynamic client review archives to custom views.
"""

from django.urls import path
from . import views

app_name = "testimonials"

urlpatterns = [
    # Global Certified Reviews Feed Page
    path("", views.TestimonialListView.as_view(), name="list"),
]