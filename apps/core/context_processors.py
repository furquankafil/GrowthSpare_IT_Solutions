# FILE: apps/core/context_processors.py
"""
Global context processors injection script for dynamic corporate configuration,
providing central accessibility to system-wide branding metrics.
"""

from urllib.parse import quote_plus

from django.conf import settings


def company_branding(request):
    """
    Exposes essential corporate variables globally across all templates,
    enforcing consistent meta metrics, contact elements, and footer anchors.
    """
    return {
        "COMPANY_NAME": "GrowthSpare IT Solutions",
        "TAGLINE": "Empowering Businesses with AI, Software Development & Digital Innovation.",
        "FOUNDER_NAME": "Mohammad Furqan Kafil",
        "OFFICIAL_EMAIL": "growthspareitsolution@gmail.com",
        "OFFICIAL_PHONE": "+91 9811579273",
        "OFFICIAL_WHATSAPP": "+91 9811579273",
        # Digits-only variant for wa.me links — wa.me rejects URLs containing
        # "+" or spaces, so this is what every wa.me href should interpolate
        # instead of OFFICIAL_WHATSAPP directly.
        "OFFICIAL_WHATSAPP_LINK": "919811579273",
        # Address is configurable via the OFFICIAL_LOCATION_ADDRESS env var
        # (see config/settings/base.py) instead of being hardcoded here.
        "OFFICIAL_LOCATION": settings.OFFICIAL_LOCATION_ADDRESS,
        "SITE_URL": "https://growthspareitsolutions.com",
        # Keyless Google Maps embed URL, built from GOOGLE_MAPS_EMBED_QUERY.
        # Uses the official /maps/embed endpoint (rather than the legacy
        # maps.google.com/maps?...&output=embed form), which is what Google
        # actually serves for iframe embeds without an API key.
        "GOOGLE_MAPS_EMBED_SRC": (
            f"https://www.google.com/maps?q={quote_plus(settings.GOOGLE_MAPS_EMBED_QUERY)}"
            "&t=&z=15&ie=UTF8&iwloc=&output=embed"
        ),
    }