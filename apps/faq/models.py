"""
Database models representing generic platform FAQs, categories, and priority sorts
supporting organized, high-performance accordion interface blocks.
"""

from django.db import models
from django.utils.text import slugify


class FAQCategory(models.Model):
    """Categorizes global FAQs to allow streamlined tabbed filtering systems."""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ascending sort order priority.",
    )

    class Meta:
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class FAQItem(models.Model):
    """
    Core dynamic accordion model holding general technical queries, business-first
    SLA statements, or general process answers.
    """
    category = models.ForeignKey(
        FAQCategory,
        on_delete=models.PROTECT,
        related_name="faqs",
        help_text="Primary grouping topic.",
    )
    question = models.CharField(
        max_length=255,
        help_text="The exact query or question statement.",
    )
    answer = models.TextField(
        help_text="The explanatory descriptive copy answer.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Priority ordering inside category accordion containers.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls visual display metrics on pages index accordions.",
    )

    class Meta:
        verbose_name = "FAQ Accordion Item"
        verbose_name_plural = "FAQ Accordion Items"
        ordering = ["order", "id"]

    def __str__(self):
        return f"[{self.category.name}] - {self.question[:50]}..."