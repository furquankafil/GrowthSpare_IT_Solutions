"""
Contact form definitions bound to models, structured for crispy form validation
and corporate layout rendering engines.
"""

from django import forms
from .models import ContactMessage
from .throttling import make_form_timestamp


class ContactForm(forms.ModelForm):
    """
    Client inquiry capture form, configured with explicit choices and help hints
    to collect cleanly structured B2B leads.

    `website` is a hidden honeypot field (real visitors never see or fill it)
    and `form_timestamp` is a signed render timestamp used server-side to reject
    submissions posted unrealistically fast after the page loaded. Both are
    non-model fields, so they never touch the database.
    """

    website = forms.CharField(
        required=False,
        label="",
        widget=forms.TextInput(
            attrs={
                # Off-screen rather than display:none so scraping bots still
                # see and fill it, while humans never interact with it.
                "style": (
                    "position:absolute!important;left:-9999px;top:-9999px;"
                    "height:1px;width:1px;overflow:hidden;opacity:0;"
                ),
                "tabindex": "-1",
                "autocomplete": "off",
                "aria-hidden": "true",
            }
        ),
    )

    form_timestamp = forms.CharField(
        required=False,
        label="",
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "company", "budget", "service", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "John Doe"}),
            "email": forms.EmailInput(attrs={"placeholder": "name@company.com"}),
            "phone": forms.TextInput(attrs={"placeholder": "+91 98115 79273"}),
            "company": forms.TextInput(attrs={"placeholder": "GrowthSpare IT Solutions"}),
            "message": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Tell us about your technical project goals, timeline parameters, or system integration bottlenecks...",
                    "class": "resize-none",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.is_bound:
            # Every freshly rendered form carries a signed timestamp proving
            # when the page was served; on POST the posted value wins over
            # initial data, so retries keep the original render time.
            self.initial.setdefault("form_timestamp", make_form_timestamp())

    def clean_phone(self):
        """Sanitizes telephone digits to prevent simple form injections."""
        phone = self.cleaned_data.get("phone", "").strip()
        # Ensure input holds standard phone numerical coordinates
        clean_digits = [char for char in phone if char.isdigit() or char in "+-() "]
        if len(clean_digits) < 7:
            raise forms.ValidationError("Please provide a valid contact telephone number.")
        return "".join(clean_digits)
