"""
URL configurations mapping workspace dashboards, stats metrics interfaces,
and client portal hubs to custom class-based views.
"""

from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    # General Operations & Client Workspace Dashboard Home
    path("", views.DashboardIndexView.as_view(), name="index"),

    # Previously-unwired dashboard-shell pages — templates existed, no routes did
    path("profile/", views.DashboardProfileView.as_view(), name="profile"),
    path("settings/", views.DashboardSettingsView.as_view(), name="settings"),
    path("users/", views.DashboardUsersView.as_view(), name="users"),
]