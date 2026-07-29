"""
Class-based views managing strategic scoping consultation bookings, form validation,
multi-step context tracking, and immediate administrative calendar alert dispatches.
"""

from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django_ratelimit.decorators import ratelimit

from .forms import ConsultationBookingForm


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class ConsultationBookingView(FormView):
    """
    Renders corporate consultation scoping funnels and handles incoming POST data streams.
    Saves consultation profiles securely and triggers calendar notification alerts.
    Rate-limited to 5 POSTs/minute per IP.
    """
    template_name = "consultation/book_form.html"
    form_class = ConsultationBookingForm
    success_url = reverse_lazy("consultation:book")

    def form_valid(self, form):
        # Save consultation metrics to the database
        booking = form.save()

        # Dispatch strategic email notification to administrators
        self.send_scoping_notification_email(booking)

        messages.success(
            self.request,
            "Your strategic scoping profile has been logged successfully! "
            "Our corporate coordination desk will review your details and confirm "
            "a meeting slot along with your video conference link.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "An error occurred during submission. Please check your data fields and try again.",
        )
        return super().form_invalid(form)

    def send_scoping_notification_email(self, booking):
        """Sends an immediate internal notification detailing scoping metrics and timing parameters."""
        subject = f"[Consultation Scheduled] {booking.name} - {booking.company or 'SME Stakeholder'}"
        body = (
            f"Admins, a new strategic consultation request has been recorded:\n\n"
            f"Name: {booking.name}\n"
            f"Email: {booking.email}\n"
            f"Phone: {booking.phone}\n"
            f"Company: {booking.company or 'N/A'}\n"
            f"Industry Focus: {booking.industry or 'N/A'}\n"
            f"Selected Service Group: {booking.get_services_required_display()}\n"
            f"Stated Budget Scale: {booking.get_budget_display()}\n"
            f"Preferred Contact Time: {booking.get_preferred_contact_time_display()}\n\n"
            f"Detailed Requirements Statement:\n{booking.project_details}\n\n"
            f"Configure and confirm this meeting inside the administrative database directly:\n"
            f"https://growthspareitsolutions.com/admin/consultation/consultationbooking/{booking.pk}/change/\n\n"
            f"Respectfully,\n"
            f"Calendar Coordinator, GrowthSpare IT Solutions"
        )
        try:
            send_mail(
                subject,
                body,
                "GrowthSpare IT Solutions <growthspareitsolution@gmail.com>",
                ["growthspareitsolution@gmail.com"],
                fail_silently=True,
            )
        except Exception:
            # Prevents email daemon runtime errors from blocking primary database saves
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dynamic SEO configurations
        context["seo_title"] = "Book a Free AI & Web Solutions Scoping Consultation"
        context["seo_description"] = (
            "Coordinate a direct, strategic scoping meeting with our solution "
            "architects. Define your requirements, budget configurations, and technical timeline parameters."
        )
        return context