"""
Administrative dashboard definitions for custom User accounts and Profile details,
integrating inlines for synchronized enterprise-level client tracking.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserProfile
from .forms import CustomUserCreationForm, CustomUserChangeForm


class UserProfileInline(admin.StackedInline):
    """Integrates detailed profile records directly within the user account editor view."""
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Associated User Profile Details"
    fk_name = "user"
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "avatar",
                    "designation",
                    "bio",
                    "website",
                    "linkedin_profile",
                )
            },
        ),
        (
            "Contact Coordinates",
            {
                "fields": (
                    "address",
                    "city",
                    "country",
                )
            },
        ),
    )


class CustomUserAdmin(UserAdmin):
    """
    Hardened admin console controller managing custom roles, WhatsApp opt-ins,
    and email verification flags directly alongside built-in Django attributes.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User
    inlines = (UserProfileInline,)

    # Columns visible on primary database listings index
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "role",
        "is_email_verified",
        "whatsapp_opt_in",
        "is_staff",
    )
    
    # Columns providing multi-variable filters on dashboard index sidebar
    list_filter = (
        "role",
        "is_email_verified",
        "whatsapp_opt_in",
        "is_staff",
        "is_active",
    )
    
    # Fields driving global database search engine searches
    search_fields = (
        "email",
        "username",
        "first_name",
        "last_name",
        "company_name",
    )
    
    ordering = ("-date_joined",)

    # Overridden field layouts supporting standard and custom authentication variables
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Identity Info", {"fields": ("first_name", "last_name", "email")}),
        ("Professional Status", {"fields": ("role", "company_name", "phone_number")}),
        ("Permissions & Checks", {"fields": ("is_active", "is_staff", "is_superuser", "is_email_verified", "whatsapp_opt_in")}),
        ("System Timestamps", {"fields": ("last_login", "date_joined")}),
    )

    # Overridden field layouts supporting dynamic custom creator modal popup
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password",
                    "first_name",
                    "last_name",
                    "role",
                    "company_name",
                    "phone_number",
                    "whatsapp_opt_in",
                    "is_active",
                ),
            },
        ),
    )


# Standard registration bindings to custom controllers
admin.site.register(User, CustomUserAdmin)