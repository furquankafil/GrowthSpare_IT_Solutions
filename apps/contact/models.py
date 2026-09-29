"""
Database models representing B2B communication targets, lead capturing metadata,
and status tracking properties matching basic pipeline architectures.
"""

from django.core.exceptions import ValidationError
from django.db import models


class ContactMessage(models.Model):
    """
    Saves incoming general business inquiry data streams directly to the database,
    providing CRM-ready records of target budgets and service selections.
    """
    BUDGET_CHOICES = (
        ("30k_50k", "₹30,000 – ₹50,000"),
        ("50k_75k", "₹50,000 – ₹75,000"),
        ("75k_1l", "₹75,000 – ₹1,00,000"),
        ("1l_1_5l", "₹1,00,000 – ₹1,50,000"),
        ("1_5l_2l", "₹1,50,000 – ₹2,00,000"),
        ("2l_plus", "₹2,00,000+"),
    )
    
    SERVICE_CHOICES = (
        ("web_dev", "Website Development"),
        ("app_dev", "Web Application Development"),
        ("ai_automation", "AI & WhatsApp Automation"),
        ("saas_erp", "SaaS & CRM/ERP Development"),
        ("digital_marketing", "SEO & Digital Marketing"),
        ("cloud_devops", "Cloud & DevOps Solutions"),
        ("other", "Custom Architectural Requirement"),
    )

    # Internal lead pipeline states: fresh leads, leads sales has reviewed,
    # and submissions the anti-spam layer or an administrator classified as spam.
    STATUS_NEW = "new"
    STATUS_PROCESSED = "processed"
    STATUS_SPAM = "spam"
    STATUS_CHOICES = (
        (STATUS_NEW, "New"),
        (STATUS_PROCESSED, "Processed"),
        (STATUS_SPAM, "Spam"),
    )

    # Machine-readable reasons a lead carries the Spam status.
    REASON_DUPLICATE = "duplicate_submission"
    REASON_MANUAL = "manual"

    name = models.CharField(
        max_length=100,
        help_text="Inquirer's identity name.",
    )
    email = models.EmailField(
        help_text="Inquirer's contact email address.",
    )
    phone = models.CharField(
        max_length=20,
        help_text="Standard contact telephone parameter.",
    )
    company = models.CharField(
        max_length=150,
        blank=True,
        help_text="Company or corporate context entity name.",
    )
    budget = models.CharField(
        max_length=50,
        choices=BUDGET_CHOICES,
        help_text="Allocated project resource scale limits.",
    )
    service = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES,
        help_text="The target corporate solution requested.",
    )
    message = models.TextField(
        max_length=2000,
        help_text="The core custom project scope statement.",
    )
    
    # Administrative tracking flags to scale into a custom CRM
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_NEW,
        db_index=True,
        help_text="Pipeline state: New, Processed, or Spam.",
    )
    spam_reason = models.CharField(
        max_length=64,
        blank=True,
        default="",
        help_text="Why this lead carries the Spam status (empty for normal leads).",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Submitting client IP (server-side abuse forensics; admin only).",
    )
    is_processed = models.BooleanField(
        default=False,
        help_text="Legacy mirror of status=Processed, kept for older queries.",
    )
    admin_notes = models.TextField(
        blank=True,
        max_length=1000,
        help_text="Internal notes during administrative processing.",
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Contact Message"
        verbose_name_plural = "Contact Messages"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Lead: {self.name} - {self.company or 'SME'} ({self.get_service_display()})"

    def save(self, *args, **kwargs):
        # The tri-state status is authoritative; keep the legacy boolean mirror
        # coherent so older dashboards/queries filtering on is_processed still work.
        self.is_processed = self.status == self.STATUS_PROCESSED
        super().save(*args, **kwargs)


class AbuseBlock(models.Model):
    """
    Administratively configured blocklist for abusive contact identifiers.

    Entries are ONLY created by a staff member from the admin panel (manual
    review) — the system never blocks an identifier automatically from a single
    suspicious submission. Values are normalized on save so lookups always
    compare like-for-like. IPs and identifiers recorded here are never exposed
    outside the admin interface.
    """

    KIND_EMAIL = "email"
    KIND_PHONE = "phone"
    KIND_IP = "ip"
    KIND_CHOICES = (
        (KIND_EMAIL, "Email address"),
        (KIND_PHONE, "Phone number"),
        (KIND_IP, "IP address"),
    )

    kind = models.CharField(
        max_length=10,
        choices=KIND_CHOICES,
        help_text="Identifier type this entry blocks.",
    )
    value = models.CharField(
        max_length=255,
        help_text="Normalized identifier value (lowercase email / digits / canonical IP).",
    )
    reason = models.CharField(
        max_length=255,
        blank=True,
        default="",
        help_text="Internal justification recorded by staff.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Inactive entries are retained for history but never match.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Abuse Block"
        verbose_name_plural = "Abuse Blocks"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "value"],
                name="unique_abuse_block_identifier",
            ),
        ]

    def __str__(self):
        return f"Block {self.get_kind_display()}: {self.value}"

    def clean(self):
        # Deferred import: apps.contact.throttling imports this module.
        from .throttling import normalize_block_value

        normalized = normalize_block_value(self.kind, self.value)
        if not normalized:
            raise ValidationError({"value": "Enter a valid identifier to block."})
        self.value = normalized

    @classmethod
    def block_identifier(cls, kind, value, reason=""):
        """Normalize and upsert an active block. Returns the row or None if empty."""
        from .throttling import normalize_block_value

        normalized = normalize_block_value(kind, value)
        if not normalized:
            return None
        obj, _created = cls.objects.update_or_create(
            kind=kind,
            value=normalized,
            defaults={"reason": reason, "is_active": True},
        )
        return obj