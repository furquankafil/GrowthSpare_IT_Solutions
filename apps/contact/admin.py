"""
Administrative control panel configurations for managing incoming client leads,
general inquiries, and process states inside pipeline systems.
"""

from django.contrib import admin
from .models import AbuseBlock, ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Control room interface managing active system leads, reviewing client budgets,
    service interests, and logging custom processing notes. Spam handling is
    first-class: suspicious rows carry the Spam status (plus why), staff can
    flag/unflag in bulk, and can block the underlying identifiers.
    """
    list_display = (
        "name",
        "email",
        "phone",
        "company",
        "service",
        "budget",
        "status",
        "spam_reason",
        "created_at",
    )
    list_filter = ("status", "spam_reason", "service", "budget", "created_at")
    search_fields = ("name", "email", "phone", "company", "message", "admin_notes", "ip_address")
    # created_at / ip_address / is_processed are server-managed: created by the
    # submission pipeline, never edited by hand (is_processed mirrors `status`).
    readonly_fields = ("created_at", "ip_address", "is_processed")

    actions = [
        "mark_as_processed",
        "mark_as_unprocessed",
        "mark_as_spam",
        "unmark_as_spam",
        "block_selected_identities",
    ]

    fieldsets = (
        (
            "Client Profile & Coordinates",
            {
                "fields": (
                    "name",
                    "email",
                    "phone",
                    "company",
                    "ip_address",
                )
            },
        ),
        (
            "Lead Scope Details",
            {
                "fields": (
                    "service",
                    "budget",
                    "message",
                    "created_at",
                )
            },
        ),
        (
            "Internal Process Controls",
            {
                "fields": (
                    "status",
                    "spam_reason",
                    "is_processed",
                    "admin_notes",
                )
            },
        ),
    )

    def mark_as_processed(self, request, queryset):
        """Action method to flag leads as processed in bulk."""
        updated = queryset.update(
            status=ContactMessage.STATUS_PROCESSED, is_processed=True
        )
        self.message_user(request, f"Successfully flagged {updated} inquiries as processed.")
    mark_as_processed.short_description = "Mark selected inquiries as processed"

    def mark_as_unprocessed(self, request, queryset):
        """Action method to flag leads as unprocessed/pending in bulk."""
        updated = queryset.update(
            status=ContactMessage.STATUS_NEW, is_processed=False, spam_reason=""
        )
        self.message_user(request, f"Successfully flagged {updated} inquiries as pending/unprocessed.")
    mark_as_unprocessed.short_description = "Mark selected inquiries as pending"

    def mark_as_spam(self, request, queryset):
        """Action method to move selected leads into the Spam state."""
        updated = queryset.update(
            status=ContactMessage.STATUS_SPAM,
            spam_reason=ContactMessage.REASON_MANUAL,
            is_processed=False,
        )
        self.message_user(request, f"Successfully flagged {updated} inquiries as spam.")
    mark_as_spam.short_description = "Mark selected inquiries as spam"

    def unmark_as_spam(self, request, queryset):
        """Action method to return wrongly-flagged leads to the normal pipeline."""
        updated = queryset.filter(status=ContactMessage.STATUS_SPAM).update(
            status=ContactMessage.STATUS_NEW, is_processed=False, spam_reason=""
        )
        self.message_user(request, f"Successfully returned {updated} inquiries to the normal pipeline.")
    unmark_as_spam.short_description = "Unmark selected inquiries as spam (restore as new)"

    def block_selected_identities(self, request, queryset):
        """
        Manual blocklist action: blocks the email/phone/IP of the selected
        leads. Blocks are only ever created this way — deliberate staff review,
        never automatically from a single suspicious message.
        """
        created = 0
        for lead in queryset:
            for kind, value in (
                (AbuseBlock.KIND_EMAIL, lead.email),
                (AbuseBlock.KIND_PHONE, lead.phone),
                (AbuseBlock.KIND_IP, lead.ip_address),
            ):
                if AbuseBlock.block_identifier(
                    kind, value, reason=f"Blocked from contact lead #{lead.pk}"
                ):
                    created += 1
        self.message_user(
            request,
            f"Blocklist updated for {queryset.count()} lead(s): {created} identifier entry(ies) active.",
        )
    block_selected_identities.short_description = (
        "Block email/phone/IP of selected inquiries"
    )


@admin.register(AbuseBlock)
class AbuseBlockAdmin(admin.ModelAdmin):
    """
    Manageable blocklist of abusive identifiers. Values are normalized on save
    and never rendered outside this admin interface.
    """
    list_display = ("kind", "value", "is_active", "reason", "created_at")
    list_filter = ("kind", "is_active")
    search_fields = ("value", "reason")
    readonly_fields = ("created_at",)
    actions = ["deactivate_selected", "reactivate_selected"]

    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"Deactivated {updated} blocklist entry(ies).")
    deactivate_selected.short_description = "Deactivate selected blocks (keep history)"

    def reactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"Reactivated {updated} blocklist entry(ies).")
    reactivate_selected.short_description = "Reactivate selected blocks"
