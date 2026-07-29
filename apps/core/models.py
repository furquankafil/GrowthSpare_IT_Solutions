"""
Database models representing generic core components, such as sitemap definitions,
newsletter validation pools, and structural platform dependencies.
"""

from django.db import models


class NewsletterSubscriber(models.Model):
    """
    Subscribes users to continuous platform bulletins, service updates,
    and technical growth publications. Tracks opt-in verification logs.
    """
    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "This email address is already subscribed to our newsletter.",
        },
        help_text="The target communication email channel.",
    )
    subscribed_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp logging subscription registration.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Enables administrative pause states for specific targets.",
    )

    class Meta:
        verbose_name = "Newsletter Subscriber"
        verbose_name_plural = "Newsletter Subscribers"
        ordering = ["-subscribed_at"]

    def __str__(self):
        return f"{self.email} (Active: {self.is_active})"


class ClientLogo(models.Model):
    """
    Represents a client/partner company shown in the homepage "Trusted by
    growing businesses..." strip. Admin-editable so real logos can be
    uploaded without touching code. If no logo image is uploaded, the
    template falls back to a premium static SVG wordmark placeholder for
    known demo clients, or an initials badge as the final fallback.
    """

    # Explicit, hand-curated map of demo/placeholder client names to a
    # premium SVG wordmark shipped under static/images/clients/. Kept as a
    # literal dict (rather than slugifying `name` at render time) so that
    # {% static %} always resolves to a file that actually exists in the
    # static manifest — arbitrary admin-added clients safely fall back to
    # the initials badge instead of risking a broken static file lookup.
    STATIC_PLACEHOLDER_LOGOS = {
        "DataCore Systems": "images/clients/datacore-systems.svg",
        "Arvex Retail": "images/clients/arvex-retail.svg",
        "Nexora Logistics": "images/clients/nexora-logistics.svg",
        "Velunex Textiles": "images/clients/velunex-textiles.svg",
        "Skyline Ventures": "images/clients/skyline-ventures.svg",
        "Primeon Manufacturing": "images/clients/primeon-manufacturing.svg",
    }

    name = models.CharField(
        max_length=100,
        help_text="Client/partner company name. Used as image alt text and as the source for the fallback initials badge.",
    )
    logo = models.ImageField(
        upload_to="clients/logos/",
        blank=True,
        null=True,
        help_text="Company logo (PNG/SVG/JPG, transparent background recommended). "
                   "Leave empty to display an automatic initials badge instead.",
    )
    website_url = models.URLField(
        blank=True,
        help_text="Optional link to the client's website when the logo is clicked.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ascending sort order priority.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether this logo is displayed on the public homepage.",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Client Logo"
        verbose_name_plural = "Client Logos"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def get_initials(self):
        """Builds a 1-2 letter fallback badge (e.g. 'Datacore Ltd' -> 'DL')."""
        parts = [p for p in self.name.split() if p]
        initials = "".join(p[0] for p in parts[:2]).upper()
        return initials or "?"

    def get_static_placeholder(self):
        """
        Returns the static-file relative path (e.g. 'images/clients/arvex-retail.svg')
        for known demo clients, or None if this client isn't in the curated map —
        in which case the template falls back to the initials badge.
        """
        return self.STATIC_PLACEHOLDER_LOGOS.get(self.name)