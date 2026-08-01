"""
Class-based views managing lead capturing pipelines, form validations,
SLA messages feedback, and asynchronous administrative alert dispatches.
"""

from django.contrib import messages
from django.core.mail import send_mail
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django_ratelimit.decorators import ratelimit

from .forms import ContactForm


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class ContactView(FormView):
    """
    Renders corporate contact entry screens and handles POST ingestion streams.
    Saves leads securely and triggers automated administrative notification emails.
    Rate-limited to 5 POSTs/minute per IP.
    """
    template_name = "contact/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:contact")

    def form_valid(self, form):
        # Save model data to database
        contact_message = form.save()

        # Trigger administrative alert notification
        self.send_lead_alert_email(contact_message)

        messages.success(
            self.request,
            "Your structural business brief has been logged successfully. "
            "Our engineering solutions architects will review your project parameters.",
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(
            self.request,
            "An error occurred during submission. Please verify your data metrics.",
        )
        return super().form_invalid(form)

    def send_lead_alert_email(self, lead):
        """Sends an immediate internal email notification containing new inquiry parameters."""
        subject = f"[New Lead] {lead.name} from {lead.company or 'SME Client'}"
        body = (
            f"Admins, a new business inquiry has been recorded:\n\n"
            f"Name: {lead.name}\n"
            f"Email: {lead.email}\n"
            f"Phone: {lead.phone}\n"
            f"Company: {lead.company or 'N/A'}\n"
            f"Selected Service: {lead.get_service_display()}\n"
            f"Stated Budget Range: {lead.get_budget_display()}\n\n"
            f"Detailed Scope Statement:\n{lead.message}\n\n"
            f"Access administrative panel to process this contact message directly:\n"
            f"https://growthspareitsolutions.com/admin/contact/contactmessage/{lead.pk}/change/\n\n"
            f"Respectfully,\n"
            f"Lead Capture Daemon, GrowthSpare IT Solutions"
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
            # Prevent email driver configuration exceptions from halting primary database saves
            pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Dynamic SEO configurations
        context["seo_title"] = "Contact our Engineering Architects & Project Offices"
        context["seo_description"] = (
            "Initiate a design brief with GrowthSpare IT Solutions. Contact our "
            "offices in New Delhi, India for custom Django, AI automation, or CRM engineering services."
        )
        return context