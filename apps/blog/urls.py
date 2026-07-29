"""
URL configurations mapping editorial listings, category filter directories,
article detail views, and async comment post targets to custom controllers.
"""

from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    # Main Publications Feed Directory
    path("", views.BlogListView.as_view(), name="list"),
    
    # Custom Dynamic Publication Detail Page
    path("<slug:slug>/", views.BlogPostDetailView.as_view(), name="detail"),
    
    # Secured Comment Ingestion Gateway Endpoint
    path("<slug:slug>/comment/", views.CommentCreateView.as_view(), name="comment_create"),
]