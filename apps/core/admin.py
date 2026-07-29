from django.contrib import admin
from django.utils.html import format_html
from .models import NewsletterSubscriber, ClientLogo


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ("email", "is_active", "subscribed_at")
    list_filter = ("is_active", "subscribed_at")
    search_fields = ("email",)
    ordering = ("-subscribed_at",)


@admin.register(ClientLogo)
class ClientLogoAdmin(admin.ModelAdmin):
    """Admin console for managing homepage "Trusted by" client/partner logos."""
    list_display = ("name", "logo_preview", "website_url", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("order", "name")

    def logo_preview(self, obj):
        if obj.logo:
            return format_html(
                '<img src="{}" style="height:32px;width:auto;border-radius:4px;" />',
                obj.logo.url,
            )
        return format_html(
            '<span style="display:inline-block;padding:4px 8px;border-radius:4px;'
            'background:#e2e8f0;font-weight:700;font-size:11px;">{}</span>',
            obj.get_initials(),
        )
    logo_preview.short_description = "Preview"
