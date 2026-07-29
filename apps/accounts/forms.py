"""
ModelForms definitions for registration, profile updates, and core 
account management matching standard crispy formatting templates.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User, UserProfile


class UserRegisterForm(UserCreationForm):
    """
    Client registration form incorporating essential B2B profiling attributes
    such as company context, WhatsApp authorization, and direct contact numbers.
    """
    first_name = forms.CharField(max_length=30, required=True, help_text="Given Name")
    last_name = forms.CharField(max_length=30, required=True, help_text="Family Name")
    email = forms.EmailField(required=True, help_text="Corporate email address")
    phone_number = forms.CharField(max_length=20, required=True, help_text="Mobile / Phone")
    company_name = forms.CharField(max_length=150, required=False, help_text="Business Entity Name")
    whatsapp_opt_in = forms.BooleanField(
        required=False,
        initial=True,
        label="Receive notifications and alerts directly via WhatsApp",
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "first_name",
            "last_name",
            "email",
            "phone_number",
            "company_name",
            "whatsapp_opt_in",
        )

    def clean_email(self):
        """Validates that the provided email is structurally unique within our records."""
        email = self.cleaned_data.get("email").lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user account is already registered with this email address.")
        return email


class UserAccountUpdateForm(forms.ModelForm):
    """Form to manage core identity changes inside the dashboard settings panel."""
    class Meta:
        model = User
        fields = ("first_name", "last_name", "phone_number", "company_name")


class UserProfileUpdateForm(forms.ModelForm):
    """Form to modify personal designations, contact criteria, and professional coordinates."""
    class Meta:
        model = UserProfile
        fields = (
            "avatar",
            "designation",
            "bio",
            "website",
            "linkedin_profile",
            "address",
            "city",
            "country",
        )
        widgets = {
            "bio": forms.Textarea(attrs={"rows": 3, "class": "resize-none"}),
        }


class CustomUserCreationForm(UserCreationForm):
    """Overridden Admin Console creator matching custom email-login credentials."""
    class Meta:
        model = User
        fields = ("email", "username", "role", "is_active", "is_staff")


class CustomUserChangeForm(UserChangeForm):
    """Overridden Admin Console modifier matching custom email-login credentials."""
    class Meta:
        model = User
        fields = ("email", "username", "role", "is_active", "is_staff")