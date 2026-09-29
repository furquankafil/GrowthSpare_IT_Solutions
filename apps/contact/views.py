"""
Class-based views managing lead capturing pipelines, form validations,
SLA messages feedback, and asynchronous administrative alert dispatches.
"""

import logging

from django.contrib import messages
from django.conf import settings
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.generic import FormView
from django_ratelimit.decorators import ratelimit

from apps.core.utils import send_mail_background

from .forms import ContactForm
from .models import ContactMessage
from .throttling import (
    find_duplicate,
    get_client_ip,
    honeypot_triggered,
    is_blocked,
    is_rate_limited,
    submission_too_fast,
)

logger = logging.getLogger(__name__)


@method_decorator(
    ratelimit(key="ip", rate="5/m", method="POST", block=True),
    name="post"
)
class ContactView(FormView):
    """
    Renders corporate contact entry screens and handles POST ingestion streams.
    Saves leads securely and triggers automated administrative notification emails.
    """

    template_name = "contact/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact:contact")

    # Generic copy shown for every anti-spam rejection: readable for a human,
    # but reveals none of the specific rules that triggered it.
    REJECTION_MESSAGE = (
        "We could not process this submission right now. "
        "Please wait a moment and try again."
    )

    def form_valid(self, form):

        client_ip = get_client_ip(self.request)
        email = form.cleaned_data.get("email", "")
        phone = form.cleaned_data.get("phone", "")
        company = form.cleaned_data.get("company", "")
        body = form.cleaned_data.get("message", "")

        # Layer 1-2: honeypot + submission speed. Silent rejection — no record,
        # no rule-specific feedback, nothing that helps an automated client
        # learn what tripped the check.
        if honeypot_triggered(form) or submission_too_fast(
            form.cleaned_data.get("form_timestamp", "")
        ):
            logger.info("Contact form submission rejected by spam heuristics")
            return self.form_invalid(form)

        # Layer 3: identifiers explicitly blocked by staff in the admin panel.
        if is_blocked(email, phone, client_ip):
            logger.info("Contact form submission from a blocked identifier")
            form.add_error(None, self.REJECTION_MESSAGE)
            return self.form_invalid(form)

        # Layer 4: duplicates. The first repeat is stored flagged as Spam for
        # admin review instead of entering the lead pipeline; later repeats are
        # dropped so hammering the form cannot grow the table.
        duplicate = find_duplicate(email, phone, body, company)
        if duplicate is not None:
            if not (
                duplicate.status == ContactMessage.STATUS_SPAM
                and duplicate.spam_reason == ContactMessage.REASON_DUPLICATE
            ):
                self.save_spam_record(form, client_ip, ContactMessage.REASON_DUPLICATE)
                logger.info("Duplicate contact submission flagged as spam")
            form.add_error(None, settings.CONTACT_RATE_LIMIT_MESSAGE)
            return self.form_invalid(form)

        # Layer 5: identity/IP rate window — rejected outright, no record.
        if is_rate_limited(self.request, email, phone):
            form.add_error(None, settings.CONTACT_RATE_LIMIT_MESSAGE)
            return self.form_invalid(form)

        # Clean submission: save model data with source IP for admin forensics.
        contact_message = form.save(commit=False)
        contact_message.ip_address = client_ip or None
        contact_message.save()

        # Send email in background (does not delay response)
        self.send_lead_alert_email(contact_message)

        messages.success(
            self.request,
            "Your structural business brief has been logged successfully. "
            "Our engineering solutions architects will review your project parameters.",
        )

        return super().form_valid(form)


    def save_spam_record(self, form, client_ip, reason):
        """Persist a submission flagged as Spam (pipeline-excluded, admin reviewable)."""
        data = form.cleaned_data
        return ContactMessage.objects.create(
            name=data.get("name", ""),
            email=data.get("email", ""),
            phone=data.get("phone", ""),
            company=data.get("company", "") or "",
            budget=data.get("budget", ""),
            service=data.get("service", ""),
            message=data.get("message", ""),
            status=ContactMessage.STATUS_SPAM,
            spam_reason=reason,
            ip_address=client_ip or None,
        )


    def form_invalid(self, form):

        messages.error(
            self.request,
            "An error occurred during submission. Please verify your data metrics.",
        )

        return super().form_invalid(form)


    def send_lead_alert_email(self, lead):

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
            f"Access administrative panel:\n"
            f"https://growthspareitsolutions.com/admin/contact/contactmessage/{lead.pk}/change/\n\n"
            f"Respectfully,\n"
            f"Lead Capture Daemon, GrowthSpare IT Solutions"
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
            "Contact GrowthSpare IT Solutions in Delhi | Free Website Audit"
        )

        context["seo_description"] = (
            "Contact GrowthSpare IT Solutions in Okhla, New Delhi — call, WhatsApp or send "
            "your project brief for websites, AI automation, CRM and SEO. Mon–Sat, 9am–7pm IST."
        )

        from django.conf import settings

        base_url = settings.SITE_URL.rstrip("/")
        context["schema_data"] = [
            {
                "@type": "LocalBusiness",
                "@id": f"{base_url}/#localbusiness",
                "name": "GrowthSpare IT Solutions",
                "url": settings.SITE_URL,
                "logo": f"{settings.SITE_URL}/static/images/logo.png",
                "image": f"{settings.SITE_URL}/static/images/logo.png",
                "description": "Contact GrowthSpare IT Solutions in Okhla, New Delhi for websites, AI automation, CRM and SEO.",
                "telephone": "+91 9811579273",
                "email": "growthspareitsolution@gmail.com",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "D-50, Shaheen Bagh, Okhla",
                    "addressLocality": "New Delhi",
                    "postalCode": "110025",
                    "addressCountry": "IN",
                },
                "openingHoursSpecification": {
                    "@type": "OpeningHoursSpecification",
                    "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
                    "opens": "09:00",
                    "closes": "19:00",
                },
                "areaServed": ["New Delhi", "South Delhi", "Noida", "Gurugram"],
                # sameAs contains ONLY the official profiles linked in the public footer.
                "sameAs": [
                    "https://www.linkedin.com/company/growthspareitsolution/",
                    "https://www.instagram.com/growthspareitsolution/",
                    "https://www.facebook.com/profile.php?id=61592462990102",
                ],
            },
            {
                "@type": "BreadcrumbList",
                "itemListElement": [
                    {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{base_url}/"},
                    {"@type": "ListItem", "position": 2, "name": "Contact", "item": f"{base_url}/contact/"},
                ],
            },
        ]

        return context