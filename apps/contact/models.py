"""
Database models representing B2B communication targets, lead capturing metadata,
and status tracking properties matching basic pipeline architectures.
"""

from django.db import models


class ContactMessage(models.Model):
    """
    Saves incoming general business inquiry data streams directly to the database,
    providing CRM-ready records of target budgets and service selections.
    """
    BUDGET_CHOICES = (
        ("under_1l", "Less than ₹1,00,000"),
        ("1l_3l", "₹1,00,000 - ₹3,00,000"),
        ("3l_5l", "₹3,00,000 - ₹5,00,000"),
        ("over_5l", "₹5,00,000+"),
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
    is_processed = models.BooleanField(
        default=False,
        help_text="Designates whether sales teams have reviewed this lead.",
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