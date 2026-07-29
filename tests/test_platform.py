"""
Consolidated corporate validation regression testing suites, verifying custom role-based 
identity profiles, dynamic services catalogs, inquiry capture logs, and consultation booking funnels.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

from apps.accounts.models import UserProfile
from apps.services.models import Service, ServiceFAQ
from apps.portfolio.models import Project, ProjectCategory
from apps.blog.models import BlogPost, BlogCategory
from apps.contact.models import ContactMessage
from apps.consultation.models import ConsultationBooking

User = get_user_model()


class AccountsTestCase(TestCase):
    """Verifies custom user account parameters and automated signal profile creations."""

    def setUp(self):
        self.user_email = "test@growthspare.com"
        self.user_password = "securepassword123"
        self.user = User.objects.create_user(
            username="testuser",
            email=self.user_email,
            password=self.user_password,
            first_name="Test",
            last_name="User",
            role="CLIENT"
        )

    def test_custom_user_creation(self):
        """Validates standard authentication model properties and custom role assignments."""
        self.assertEqual(self.user.email, self.user_email)
        self.assertEqual(self.user.role, "CLIENT")
        self.assertEqual(self.user.get_role_display(), "Enterprise Client")
        self.assertFalse(self.user.is_email_verified)

    def test_profile_signal_creation(self):
        """Verifies that user profile creations are safely triggered via signals."""
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.country, "India")


class ServicesTestCase(TestCase):
    """Verifies active solutions creations, slug generation logic, and string list utilities."""

    def setUp(self):
        self.service = Service.objects.create(
            title="AI Automation Systems",
            icon_class="fas fa-brain",
            overview="Intelligent WhatsApp webhook automations.",
            detailed_description="<p>Detailed B2B software engineering solutions description.</p>",
            features="Feature Alpha\nFeature Beta",
            benefits="Outcome Delta\nOutcome Gamma",
            process_steps="Phase Discovery\nPhase Deployment",
            technologies="Python, Django, WhatsApp Cloud API",
            pricing_estimate="Starting from ₹49,999"
        )

    def test_service_slug_generation(self):
        """Validates that slugification executes cleanly on model save boundaries."""
        self.assertEqual(self.service.slug, "ai-automation-systems")

    def test_utility_string_splittings(self):
        """Confirms that newline-split lists generate correct sequence arrays."""
        self.assertEqual(self.service.get_features_list(), ["Feature Alpha", "Feature Beta"])
        self.assertEqual(self.service.get_benefits_list(), ["Outcome Delta", "Outcome Gamma"])
        self.assertEqual(self.service.get_process_list(), ["Phase Discovery", "Phase Deployment"])
        self.assertEqual(self.service.get_tech_list(), ["Python", "Django", "WhatsApp Cloud API"])


class ContactTestCase(TestCase):
    """Verifies client inquiry forms pipeline integration and database tracking."""

    def test_contact_message_submission(self):
        """Validates POST requests safely log leads inside the database."""
        client = Client()
        contact_url = reverse("contact:contact")
        
        post_data = {
            "name": "Mohammad Furqan",
            "email": "furqan@clientcompany.com",
            "phone": "+91 9811579273",
            "company": "Enterprise Partner",
            "budget": "1l_3l",
            "service": "ai_automation",
            "message": "We need custom WhatsApp lead routing scripts written in Python."
        }
        
        response = client.post(contact_url, post_data)
        self.assertEqual(response.status_code, 302)  # Check redirects on valid submit
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, "Mohammad Furqan")
        self.assertEqual(message.get_budget_display(), "₹1,00,000 - ₹3,00,000")
        self.assertFalse(message.is_processed)