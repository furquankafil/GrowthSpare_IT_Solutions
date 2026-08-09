"""
Database models representing consultation bookings, multi-step scoping criteria,
scheduling states, and Zoom/meeting configurations matching pipeline setups.
"""

from django.db import models


class ConsultationBooking(models.Model):
    """
    Saves multi-step technical design audit submissions directly to the database,
    providing complete records of enterprise industry scope, budgets, and scheduling logistics.
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

    STATUS_CHOICES = (
        ("PENDING", "Pending Triage"),
        ("SCHEDULED", "Meeting Scheduled"),
        ("COMPLETED", "Consultation Completed"),
        ("CANCELLED", "Client Cancelled"),
    )

    TIME_CHOICES = (
        ("morning", "Morning (10:00 AM - 1:00 PM IST)"),
        ("afternoon", "Afternoon (1:00 PM - 5:00 PM IST)"),
        ("evening", "Evening (5:00 PM - 8:00 PM IST)"),
    )

    name = models.CharField(
        max_length=100,
        help_text="Primary stakeholder identity name.",
    )
    email = models.EmailField(
        help_text="Primary email for meeting notifications.",
    )
    phone = models.CharField(
        max_length=20,
        help_text="Standard contact telephone parameter.",
    )
    company = models.CharField(
        max_length=150,
        blank=True,
        help_text="Entity or company business name.",
    )
    website_url = models.URLField(
        max_length=255,
        blank=True,
        help_text="Existing website URL to be reviewed as part of the free audit (optional if the business has no site yet).",
    )
    industry = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., E-commerce, Logistics, Healthcare, FinTech.",
    )
    budget = models.CharField(
        max_length=50,
        choices=BUDGET_CHOICES,
        help_text="Allocated project resource scale limits.",
    )
    services_required = models.CharField(
        max_length=100,
        choices=SERVICE_CHOICES,
        help_text="Core service branch focus area.",
    )
    project_details = models.TextField(
        max_length=3000,
        help_text="Detailed project requirements, current tech stack, or problem statement.",
    )
    preferred_contact_time = models.CharField(
        max_length=50,
        choices=TIME_CHOICES,
        help_text="Target timezone allocation preference.",
    )
    
    # Scheduling Status parameters for dashboard / CRM integration
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
        help_text="Current process phase in CRM workspace.",
    )
    scheduled_time = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Confirmed meeting time mapping (Set by Admin).",
    )
    meeting_link = models.URLField(
        blank=True,
        null=True,
        help_text="Dynamic video-call coordinate (Zoom / Google Meet URL).",
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Consultation Booking"
        verbose_name_plural = "Consultation Bookings"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Audit Session: {self.name} - {self.company or 'SME'} ({self.get_services_required_display()})"