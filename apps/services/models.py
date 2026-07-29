"""
Database models representing dynamic corporate services, capability solutions,
associated features, tech stacks, and priority categorizations.

Configured with a Many-to-Many relationship between Services and ServiceCategories,
allowing administrators to assign multiple categories to each capability dynamically.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ServiceCategory(models.Model):
    """
    Categorizes global services to support streamlined tabbed filtering systems.
    Includes ONLY the 5 verified corporate categories:
    1. Web Solutions (web-solutions)
    2. AI Automation (ai-automation)
    3. SaaS & CRM Systems (saas-crm-systems)
    4. Digital Marketing (digital-marketing)
    5. SEO & Marketing (seo-marketing)
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ascending sort order priority.",
    )

    class Meta:
        verbose_name = "Service Category"
        verbose_name_plural = "Service Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Service(models.Model):
    """
    Core service capability schema holding the layout blocks required to render
    unique, high-performance capability pages dynamically from the database.
    """
    title = models.CharField(
        max_length=150,
        unique=True,
        help_text="e.g. Website Development, AI Automation, CRM Software Development.",
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
        help_text="Calculated automatically if left blank.",
    )
    categories = models.ManyToManyField(
        ServiceCategory,
        related_name="services",
        help_text="Select one or more categories associated with this corporate service.",
    )
    icon_class = models.CharField(
        max_length=100,
        default="fas fa-laptop-code",
        help_text="FontAwesome class icon tag representing this service (e.g., 'fas fa-brain').",
    )
    overview = models.TextField(
        help_text="Polished corporate summary statement.",
    )
    detailed_description = models.TextField(
        help_text="Detailed corporate summary block rendering rich HTML markup directly.",
    )
    
    # Newline-separated lists to structure presentation sections
    features = models.TextField(
        help_text="List of core features. Enter one item per line.",
    )
    benefits = models.TextField(
        help_text="List of competitive benefits or outcomes. Enter one item per line.",
    )
    process_steps = models.TextField(
        help_text="Workflow steps. Enter one step per line in order.",
    )
    technologies = models.CharField(
        max_length=255,
        help_text="Comma-separated development environments and software (e.g. Django, Postgres, OpenAI).",
    )
    use_cases = models.TextField(
        blank=True,
        help_text="Real-world scenarios/industries this service applies to. Enter one item per line.",
    )
    why_choose_us = models.TextField(
        blank=True,
        help_text="Reasons to choose GrowthSpare for this specific service. Enter one item per line.",
    )
    cta_headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Optional custom call-to-action headline for this service's detail page banner.",
    )
    cta_subtext = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional supporting line shown under the call-to-action headline.",
    )

    pricing_estimate = models.CharField(
        max_length=150,
        default="Starting at ₹4,999",
        help_text="Price range or starting rate placeholder statement.",
    )
    
    # Target SEO optimization headers
    meta_title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Enforces custom Title Tag override for search indexers.",
    )
    meta_description = models.TextField(
        max_length=250,
        blank=True,
        help_text="Enforces custom Meta Description override.",
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Controls visual display metrics on public-facing page indexes.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Corporate Solution"
        verbose_name_plural = "Corporate Solutions"
        ordering = ["title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Ensures system slug stays dynamically synchronized with title alterations."""
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns structural absolute route path linking to service page detail view."""
        return reverse("services:detail", kwargs={"slug": self.slug})

    # Utility string splittings to avoid complex parsing logic within template blocks
    def get_features_list(self):
        return [f.strip() for f in self.features.split("\n") if f.strip()]

    def get_benefits_list(self):
        return [b.strip() for b in self.benefits.split("\n") if b.strip()]

    def get_process_list(self):
        return [p.strip() for p in self.process_steps.split("\n") if p.strip()]

    def get_tech_list(self):
        return [t.strip() for t in self.technologies.split(",") if t.strip()]

    def get_use_cases_list(self):
        return [u.strip() for u in self.use_cases.split("\n") if u.strip()]

    def get_why_choose_list(self):
        return [w.strip() for w in self.why_choose_us.split("\n") if w.strip()]


class ServiceFAQ(models.Model):
    """
    Holds FAQs tied strictly to individual services to improve usability
    and structure information on the detail views.
    """
    service = models.ForeignKey(
        Service,
        on_delete=models.CASCADE,
        related_name="service_faqs",
        help_text="The parent capability solution.",
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ascending sort order priority.",
    )

    class Meta:
        verbose_name = "Service FAQ"
        verbose_name_plural = "Service FAQs"
        ordering = ["order", "id"]

    def __str__(self):
        return f"FAQ ({self.service.title}): {self.question[:40]}..."