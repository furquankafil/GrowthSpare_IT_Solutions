"""
URL configurations mapping project lists, filter pathways, and details pages
to custom class-based views.
"""

from django.urls import path
from . import views

app_name = "portfolio"

urlpatterns = [
    # Enterprise Case Studies Gallery
    path("", views.PortfolioListView.as_view(), name="list"),
    
    # Custom Dynamic Project Detail Page
    path("<slug:slug>/", views.ProjectDetailView.as_view(), name="detail"),
]