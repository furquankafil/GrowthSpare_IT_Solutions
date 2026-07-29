"""
URL configurations mapping lists of capability solutions and structural details pages
to custom class-based controllers.
"""

from django.urls import path
from . import views

app_name = "services"

urlpatterns = [
    # Services Catalog Main Index
    path("", views.ServiceListView.as_view(), name="list"),

    # Dedicated Category Landing Pages (e.g. /services/category/web-solutions/)
    # Kept under a "category/" prefix so a category slug can never collide
    # with an individual Service's own detail slug below.
    path("category/<slug:category_slug>/", views.ServiceCategoryView.as_view(), name="category"),

    # Custom Dynamic Service Detail Page
    path("<slug:slug>/", views.ServiceDetailView.as_view(), name="detail"),
]