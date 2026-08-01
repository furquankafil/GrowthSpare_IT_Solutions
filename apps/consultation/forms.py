"""
ModelForm definition for consultation scheduling, structured for multi-step form validation,
crispy alignment, and corporate layout formatting.
"""

from django import forms
from .models import ConsultationBooking


class ConsultationBookingForm(forms.ModelForm):
    """
    Intake form driving the technical scoping funnel. Gathers identity coordinates,
    scope parameters, and scheduling preferences directly from prospects.
    """
    class Meta:
        model = ConsultationBooking
        fields = [
            "name",
            "email",
            "phone",
            "company",
            "industry",
            "budget",
            "services_required",
            "project_details",
            "preferred_contact_time",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@company.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 9811653212"}),
            "company": forms.TextInput(attrs={"placeholder": "GrowthSpare IT Solutions"}),
            "industry": forms.TextInput(attrs={"placeholder": "e.g., E-commerce, FinTech, Logistics"}),
            "project_details": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Briefly describe your requirements, current technical bottlenecks, or software framework expectations...",
                    "class": "resize-none",
                }
            ),
        }

    def clean_phone(self):
        """Sanitizes telephone digits to prevent injection and enforce numeric integrity."""
        phone = self.cleaned_data.get("phone", "").strip()
        clean_digits = [char for char in phone if char.isdigit() or char in "+-() "]
        if len(clean_digits) < 7:
            raise forms.ValidationError("Please provide a valid contact telephone number.")
        return "".join(clean_digits)