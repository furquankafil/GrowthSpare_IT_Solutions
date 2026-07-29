"""
Database models representing dynamic editorial articles, categorical nodes,
view metrics tracking, and moderated client comment systems.
"""

from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from django.conf import settings
from django.utils import timezone


class BlogCategory(models.Model):
    """Categorizes published editorial resources, supporting focused indexing."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(models.Model):
    """
    Core blog post schema holding structural editorial copy, SEO meta,
    featured states, view counts, and dynamic reading-time values.
    """
    title = models.CharField(
        max_length=200,
        unique=True,
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.PROTECT,
        related_name="posts",
        help_text="Primary technical branch classification.",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="blog_posts",
        help_text="Author profile managing verification and credentials.",
    )
    featured_image = models.ImageField(
        upload_to="blog/featured/",
        help_text="Primary blog image asset.",
    )
    content = models.TextField(
        help_text="Markdown or rich HTML structured editorial copy.",
    )
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text="Comma-separated keyword tags.",
    )
    
    reading_time = models.PositiveIntegerField(
        blank=True,
        help_text="Calculated automatically based on content word count if empty.",
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Simple read count indicator.",
    )
    
    is_published = models.BooleanField(
        default=False,
        help_text="Controls index eligibility on public feed screens.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Promotes article to high-level layout containers.",
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Actual publishing trigger timestamp.",
    )
    
    # Dynamic SEO optimization parameters
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

    class Meta:
        verbose_name = "Blog Publication"
        verbose_name_plural = "Blog Publications"
        ordering = ["-published_at", "-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """Ensures slug, reading time estimation, and publishing timestamps stay aligned."""
        if not self.slug:
            self.slug = slugify(self.title)
            
        # Calculate dynamic reading time (standard: ~200 words per minute)
        if self.content:
            word_count = len(self.content.split())
            self.reading_time = max(1, round(word_count / 200))
        else:
            self.reading_time = 1

        # Track active publishing transition changes
        if self.is_published and not self.published_at:
            self.published_at = timezone.now()
        elif not self.is_published:
            self.published_at = None
            
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        """Returns standard absolute route path linking to blog article detail view."""
        return reverse("blog:detail", kwargs={"slug": self.slug})

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(",") if t.strip()]


class BlogComment(models.Model):
    """Moderated comment records submitted by readers."""
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name="comments",
    )
    name = models.CharField(
        max_length=100,
        help_text="Display identity name.",
    )
    email = models.EmailField(
        help_text="Primary email for tracking purposes.",
    )
    content = models.TextField(
        max_length=1000,
        help_text="The core submitted statement text.",
    )
    is_approved = models.BooleanField(
        default=False,
        help_text="Spam-prevention moderation validation status.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Blog Comment"
        verbose_name_plural = "Blog Comments"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Comment by {self.name} on {self.post.title}"