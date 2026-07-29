"""
Database models representing core custom users and extended profiles 
for identity verification, role-based access, and client workspaces.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    """
    Core authentication system model. Extends standard Django identity structure 
    to incorporate CRM-ready designations, WhatsApp tracking, and email validation status.
    """
    ROLE_CHOICES = (
        ("ADMIN", "Administrator"),
        ("MANAGER", "Project Manager"),
        ("DEVELOPER", "Software Engineer"),
        ("CLIENT", "Enterprise Client"),
    )

    email = models.EmailField(
        unique=True,
        error_messages={
            "unique": "A user with that email address already exists.",
        },
    )
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CLIENT",
        help_text="Defines workspace permissions and dashboard interfaces.",
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Standard contact phone number.",
    )
    company_name = models.CharField(
        max_length=150,
        blank=True,
        help_text="Associated business entity.",
    )
    is_email_verified = models.BooleanField(
        default=False,
        help_text="Validation flag checked during portal authorization.",
    )
    whatsapp_opt_in = models.BooleanField(
        default=False,
        help_text="Authorization check status for continuous platform updates.",
    )

    # Use email instead of default username for primary authentication
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        verbose_name = "User Account"
        verbose_name_plural = "User Accounts"
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"


class UserProfile(models.Model):
    """
    Extended user attributes mapping to custom business profiles.
    Used for profile updates, contact preferences, and CRM integration records.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        help_text="The associated master authentication credentials.",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        help_text="Profile picture for dynamic dashboards.",
    )
    designation = models.CharField(
        max_length=100,
        blank=True,
        help_text="Title or job role in the company.",
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
        help_text="Brief professional summary.",
    )
    website = models.URLField(
        blank=True,
        help_text="Corporate or personal website link.",
    )
    linkedin_profile = models.URLField(
        blank=True,
        help_text="Verified professional network link.",
    )
    address = models.CharField(
        max_length=255,
        blank=True,
    )
    city = models.CharField(
        max_length=100,
        blank=True,
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        default="India",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"Profile: {self.user.get_full_name() or self.user.username}"


# ==============================================================================
# Model Signals for Automated Profile Creation and Database Initialization
# ==============================================================================

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically constructs an extended profile upon user instantiation."""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Keeps the extended user profile synchronized during model updates."""
    instance.profile.save()