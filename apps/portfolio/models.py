"""
Database models representing project case studies, client categories,
system metrics, and supplementary gallery images.

Updated to support multi-category associations per project, allowing robust 
and flexible filtering arrays across modern enterprise divisions.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ProjectCategory(models.Model):
    """Categorizes case studies to support seamless filtering interfaces."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Project Category"
        verbose_name_plural = "Project Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(models.Model):
    """
    Core case study architecture representing unique company engagements,
    detailing structural problems, technical actions, and verified metrics.
    
    Updated to utilize a Many-to-Many relationship for categories to support 
    multi-classification metrics across dynamic filters.
    """
    title = models.CharField(
        max_length=150,
        unique=True,
    )
    slug = models.SlugField(
        max_length=180,
        unique=True,
        blank=True,
    )
    categories = models.ManyToManyField(
        ProjectCategory,
        related_name="projects",
        help_text="Select one or more categories associated with this showcase project.",
    )
    featured_image = models.URLField(
    help_text="Primary visualization card banner URL.",
    )
    video_url = models.URLField(
        blank=True,
        null=True,
        help_text="Optional embedded link showing design or code demonstrations.",
    )
    client_name = models.CharField(
        max_length=150,
        help_text="Business or corporate name.",
    )
    industry = models.CharField(
        max_length=100,
        help_text="The corporate sector targeted.",
    )
    
    # Comprehensive problem-solving narratives
    problem_statement = models.TextField(
        help_text="State of legacy structures or challenges solved.",
    )
    solution_statement = models.TextField(
        help_text="Detailed engineering architecture deployed by GrowthSpare.",
    )
    results_statement = models.TextField(
        help_text="Verified quantitative results (e.g., 200% scaling increase).",
    )
    
    technology_stack = models.CharField(
        max_length=255,
        help_text="Comma-separated development tools (e.g., Django, React, AWS).",
    )
    project_duration = models.CharField(
        max_length=50,
        help_text="Deployment timeline (e.g., 2 Months, 12 Weeks).",
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated descriptive keyword tags.",
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Enables display in landing page showcase sections.",
    )
    
    # Custom Metadata Tags for SEO
    meta_title = models.CharField(
        max_length=150,
        blank=True,
        help_text="Enforces custom Title Tag override.",
    )
    meta_description = models.TextField(
        max_length=250,
        blank=True,
        help_text="Enforces custom Meta Description override.",
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "Enterprise Case Study"
        verbose_name_plural = "Enterprise Case Studies"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.client_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns standard absolute route path linking to project details page."""
        return reverse("portfolio:detail", kwargs={"slug": self.slug})

    def get_tech_list(self):
        """Auxiliary utility splittings to decouple parsing within templating contexts."""
        return [t.strip() for t in self.technology_stack.split(",") if t.strip()]

    def get_tags_list(self):
        """Auxiliary utility splittings to decouple parsing within templating contexts."""
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class ProjectImage(models.Model):
    """Dynamic structural project screenshots and visual asset galleries."""
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="gallery_images",
        help_text="The associated case study parent model.",
    )
    image = models.ImageField(
        upload_to="portfolio/gallery/",
    )
    caption = models.CharField(
        max_length=150,
        blank=True,
        help_text="Short label shown below image inside dynamic slider containers.",
    )

    class Meta:
        verbose_name = "Project Gallery Image"
        verbose_name_plural = "Project Gallery Images"

    def __str__(self):
        return f"Gallery Asset: {self.project.title} - {self.caption or self.id}"