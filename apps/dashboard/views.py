"""
Class-based views managing operations and client dashboard interfaces, aggregated analytics,
role-based access validations, and active bulletin allocations.
"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.contrib.auth import get_user_model

# Standardized imports inside the view layer to isolate application dependencies
from apps.contact.models import ContactMessage
from apps.consultation.models import ConsultationBooking
from .models import SystemAnnouncement

User = get_user_model()


class DashboardProfileView(LoginRequiredMixin, TemplateView):
    """
    Dashboard-shell-styled profile view. Reads exclusively from request.user
    (already available in every template context), so no extra query needed.
    Distinct from accounts:profile, which renders the same identity data
    outside the dashboard shell — both remain available.
    """
    template_name = "dashboard/profile.html"


class DashboardSettingsView(LoginRequiredMixin, TemplateView):
    """
    Workspace settings overview. Display-only (credential/notification status),
    reads from request.user directly.
    """
    template_name = "dashboard/settings.html"


class DashboardUsersView(LoginRequiredMixin, TemplateView):
    """
    Team & Clients directory, restricted to ADMIN/MANAGER roles at the
    template level. Provides the real user queryset that the template
    previously had hardcoded as two static demo rows.
    """
    template_name = "dashboard/users.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.role in ["ADMIN", "MANAGER"]:
            context["directory_users"] = User.objects.all().order_by("-date_joined")[:50]
        return context


class DashboardIndexView(LoginRequiredMixin, TemplateView):
    """
    Consolidates workspace metrics, transactional statistics, and role-based views.
    Integrates system broadcasts alongside distinct client and team metrics.
    """
    template_name = "dashboard/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # Fetch active broadcasts targeted dynamically at this user's workspace
        context["announcements"] = SystemAnnouncement.objects.filter(
            is_active=True,
            target_role__in=[user.role, "ALL"]
        ).order_by("-created_at")[:5]

        # Role-Based Access Control metrics parsing
        if user.role in ["ADMIN", "MANAGER"]:
            # Aggregate system-wide analytics for operations and management teams
            context["is_staff_dashboard"] = True
            context["total_accounts"] = User.objects.count()
            context["total_leads"] = ContactMessage.objects.count()
            context["pending_bookings"] = ConsultationBooking.objects.filter(status="PENDING").count()
            context["total_bookings"] = ConsultationBooking.objects.count()
            
            # Feed real-time pipeline list tables
            context["recent_leads"] = ContactMessage.objects.all().order_by("-created_at")[:5]
            context["recent_bookings"] = ConsultationBooking.objects.all().order_by("-created_at")[:5]
            
        else:
            # Aggregate unique metrics localized strictly for B2B client experiences
            context["is_staff_dashboard"] = False
            
            # Query active client-specific consultations matching registered email coordinates
            client_bookings = ConsultationBooking.objects.filter(email=user.email)
            context["total_bookings"] = client_bookings.count()
            context["pending_bookings"] = client_bookings.filter(status="PENDING").count()
            context["scheduled_bookings"] = client_bookings.filter(status="SCHEDULED").count()
            
            # Feed recent client-specific consultation items
            context["my_bookings"] = client_bookings.order_by("-created_at")[:5]
            
        return context