"""
Class-based views managing strategic scoping consultation bookings,
multi-step context tracking, and administrative alert dispatches.
"""

from django.contrib import messages
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django_ratelimit.decorators import ratelimit

from apps.core.utils import send_mail_background

from .forms import ConsultationBookingForm


@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=True),
    name="post"
)
class ConsultationBookingView(FormView):

    template_name = "consultation/book_form.html"
    form_class = ConsultationBookingForm
    success_url = reverse_lazy("consultation:book")


    def form_valid(self, form):

        booking = form.save()

        # Background email sending
        self.send_scoping_notification_email(booking)


        messages.success(
            self.request,
            "Your free website audit request has been received! "
            "Our team will review your details and get back to you shortly "
            "with your audit findings and a suggested meeting slot.",
        )

        return super().form_valid(form)



    def form_invalid(self, form):

        messages.error(
            self.request,
            "An error occurred during submission. Please check your data fields and try again.",
        )

        return super().form_invalid(form)



    def send_scoping_notification_email(self, booking):

        subject = (
            f"[Free Website Audit Request] "
            f"{booking.name} - {booking.company or 'SME Stakeholder'}"
        )


        body = (
            f"Admins, a new free website audit request has been recorded:\n\n"
            f"Name: {booking.name}\n"
            f"Email: {booking.email}\n"
            f"Phone / WhatsApp: {booking.phone}\n"
            f"Company: {booking.company or 'N/A'}\n"
            f"Website URL: {booking.website_url or 'No existing website'}\n"
            f"Industry Focus: {booking.industry or 'N/A'}\n"
            f"Selected Service Group: {booking.get_services_required_display()}\n"
            f"Stated Budget Scale: {booking.get_budget_display()}\n"
            f"Preferred Contact Time: {booking.get_preferred_contact_time_display()}\n\n"
            f"Detailed Requirements:\n{booking.project_details}\n\n"
            f"Admin Panel:\n"
            f"https://growthspareitsolutions.com/admin/consultation/consultationbooking/{booking.pk}/change/\n\n"
            f"Respectfully,\n"
            f"Calendar Coordinator, GrowthSpare IT Solutions"
        )


        send_mail_background(
            subject,
            body,
            "GrowthSpare IT Solutions <growthspareitsolution@gmail.com>",
            ["growthspareitsolution@gmail.com"],
        )



    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        context["seo_title"] = (
            "Get a Free Website Audit - GrowthSpare IT Solutions"
        )

        context["seo_description"] = (
            "Request a free website audit from GrowthSpare IT Solutions. "
            "Share your website and business details and our team will "
            "review your online presence and get in touch."
        )

        return context