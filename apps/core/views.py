"""
Core page routing views, corporate compliance pages, async newsletter subscription endpoints,
and secure dynamic 404/500 exception handling views.
"""

from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, View
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit

from .models import NewsletterSubscriber, ClientLogo
from apps.services.models import Service
from apps.portfolio.models import Project
from apps.blog.models import BlogPost
from apps.testimonials.models import Testimonial


class HomeView(TemplateView):
    """
    Renders the premium corporate landing engine. Passes dynamic structural parameters
    including latest portfolio highlights, active service capabilities, and recent blog entries.
    """
    template_name = "core/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Load active business solutions, newest case studies, and editorial articles
        context["featured_services"] = Service.objects.filter(is_active=True).order_by("id")
        context["featured_projects"] = Project.objects.filter(is_featured=True)[:3]
        context["recent_blogs"] = BlogPost.objects.filter(is_published=True).order_by("-published_at")[:3]
        context["testimonials"] = Testimonial.objects.filter(is_active=True).select_related("project")[:6]

        # Client/partner logos for the "Trusted by" strip. Each entry renders
        # its uploaded logo image, or falls back to an initials badge in the
        # template when no logo file has been uploaded for that client.
        context["client_logos"] = ClientLogo.objects.filter(is_active=True)

        # Organization structured data — previously absent from the homepage entirely.
        context["schema_type"] = "Organization"
        context["schema_data"] = {
            "name": "GrowthSpare IT Solutions",
            "url": "https://growthspareitsolutions.com",
            "logo": "https://growthspareitsolutions.com/static/images/logo.png",
            "description": "Empowering Businesses with AI, Software Development & Digital Innovation.",
            "email": "growthspareitsolution@gmail.com",
            "telephone": "+91 9811579273",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "D-50, Shaheen Bagh, Okhla",
                "addressLocality": "New Delhi",
                "postalCode": "110025",
                "addressCountry": "IN",
            },
        }
        
        # SEO parameters
        context["seo_title"] = "Grow Smarter. Scale Faster."
        context["seo_description"] = "Empowering Businesses with AI, Software Development & Digital Innovation."
        return context


class AboutView(TemplateView):
    """Renders our company story, leadership matrices, values, and global delivery standards."""
    template_name = "core/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["seo_title"] = "Our Vision & Enterprise Engineering Leadership"
        context["seo_description"] = "Learn how GrowthSpare IT Solutions helps businesses scale globally using advanced technology."
        return context


class PrivacyPolicyView(TemplateView):
    """Corporate data security compliance page detailing handling under standard ISO protocols."""
    template_name = "core/privacy.html"


class TermsView(TemplateView):
    """Legal service level agreements and structural user operation terms."""
    template_name = "core/terms.html"


class RefundPolicyView(TemplateView):
    """Standard SLA billing, retainer timelines, and service cancellation matrices."""
    template_name = "core/refund.html"


class CookiesPolicyView(TemplateView):
    """Detailed analytics collection, persistent cookie usage, and privacy controls."""
    template_name = "core/cookies.html"


@method_decorator(ratelimit(key="ip", rate="5/m", method="POST", block=True), name="post")
class NewsletterSubscribeView(View):
    """
    Asynchronous JSON-ready subscription endpoint processing incoming marketing 
    subscription requests and logging validation records in the subscriber model.
    Rate-limited to 5 POSTs/minute per IP.
    """

    def post(self, request, *args, **kwargs):
        email = request.POST.get("email", "").strip().lower()
        if not email:
            return JsonResponse({"success": False, "message": "Email field is required."})

        # Model.save() does not run field validators — validate explicitly
        # before writing, otherwise malformed strings land straight in the DB.
        try:
            validate_email(email)
        except ValidationError:
            return JsonResponse({"success": False, "message": "Please provide a valid email address."})

        # Process subscriber save pipeline safely
        subscriber, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if not created:
            if subscriber.is_active:
                return JsonResponse({"success": True, "message": "You are already active in our newsletter loop."})
            else:
                subscriber.is_active = True
                subscriber.save()
                return JsonResponse({"success": True, "message": "Your newsletter subscription has been reactivated!"})

        return JsonResponse({"success": True, "message": "Successfully subscribed to GrowthSpare IT Solutions bulletins!"})


# ==============================================================================
# Security Exceptions & Client Failure Handlers (CBV & standard mapping)
# ==============================================================================

def health_check(request):
    """
    Lightweight liveness/readiness endpoint for Docker HEALTHCHECK, Nginx,
    and cloud platform health probes (Render, Railway, Cloud Run). Intentionally
    avoids heavy DB/cache calls so it responds fast under load.
    """
    return JsonResponse({"status": "ok"})


def custom_handler_404(request, exception=None):
    """Renders highly polished corporate 404 template with helpful navigation nodes."""
    response = render(request, "core/404.html", status=404)
    return response


def custom_handler_500(request):
    """Renders static corporate 500 failure state when internal code boundaries fail."""
    response = render(request, "core/500.html", status=500)
    return response