"""
Database models representing verified client reviews, executive statements,
star ratings, and company contexts.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Testimonial(models.Model):
    """
    Saves and structures certified corporate reviews, linking direct outcomes
    to specific customer profiles to drive global on-page social proof.
    """
    client_name = models.CharField(
        max_length=100,
        help_text="Name of the reviewing stakeholder.",
    )
    company_name = models.CharField(
        max_length=150,
        help_text="Company name representing the B2B client context.",
    )
    designation = models.CharField(
        max_length=100,
        help_text="Role or title of the stakeholder (e.g., CTO, Founder).",
    )
    client_avatar = models.ImageField(
        upload_to="testimonials/avatars/",
        blank=True,
        null=True,
        help_text="Stakeholder portrait display asset.",
    )
    review = models.TextField(
        max_length=1000,
        help_text="The core testimonial statement narrative.",
    )
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Evaluated scale ranging from 1 to 5 stars.",
    )
    
    # Decoupled string relation pointing to portfolio project model safely
    project = models.ForeignKey(
        "portfolio.Project",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="testimonials",
        help_text="Optional completed case study linkage.",
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Controls inclusion metrics inside front-end slider loops.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Ascending visual sorting priority.",
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:
        verbose_name = "Client Testimonial"
        verbose_name_plural = "Client Testimonials"
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.client_name} - {self.company_name} ({self.rating} Stars)"