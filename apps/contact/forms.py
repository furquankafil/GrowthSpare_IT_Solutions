"""
Contact form definitions bound to models, structured for crispy form validation
and corporate layout rendering engines.
"""

from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """
    Client inquiry capture form, configured with explicit choices and help hints
    to collect cleanly structured B2B leads.
    """
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "company", "budget", "service", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@company.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 9811653212"}),
            "company": forms.TextInput(attrs={"placeholder": "GrowthSpare IT Solutions"}),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us about your technical project goals, timeline parameters, or system integration bottlenecks...",
                    "class": "resize-none",
                }
            ),
        }

    def clean_phone(self):
        """Sanitizes telephone digits to prevent simple form injections."""
        phone = self.cleaned_data.get("phone", "").strip()
        # Ensure input holds standard phone numerical coordinates
        clean_digits = [char for char in phone if char.isdigit() or char in "+-() "]
        if len(clean_digits) < 7:
            raise forms.ValidationError("Please provide a valid contact telephone number.")
        return "".join(clean_digits)