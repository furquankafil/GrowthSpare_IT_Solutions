"""
Consolidated corporate validation regression testing suites, verifying custom role-based 
identity profiles, dynamic services catalogs, inquiry capture logs, and consultation booking funnels.
"""

from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings

import json
import re

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

    def setUp(self):
        # Start with empty throttle/ratelimit counters (shared test-client IP).
        cache.clear()

    def test_contact_message_submission(self):
        """Validates POST requests safely log leads inside the database."""
        client = Client()
        contact_url = reverse("contact:contact")
        
        post_data = {
            "name": "Mohammad Furqan",
            "email": "furqan@clientcompany.com",
            "phone": "+91 9811579273",
            "company": "Enterprise Partner",
            "budget": "75k_1l",
            "service": "ai_automation",
            "message": "We need custom WhatsApp lead routing scripts written in Python."
        }
        
        response = client.post(contact_url, post_data)
        self.assertEqual(response.status_code, 302)  # Check redirects on valid submit
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, "Mohammad Furqan")
        self.assertEqual(message.get_budget_display(), "₹75,000 – ₹1,00,000")
        self.assertFalse(message.is_processed)


class LocalServicePagesTestCase(TestCase):
    """Verifies the four hyper-local commercial landing pages: status, unique
    metadata, canonicals, single H1, JSON-LD graph, NAP/CTAs, and sitemap."""

    PAGES = [
        ("core:local-website-okhla", "Website Development Company in Okhla Delhi | GrowthSpare"),
        ("core:local-crm-delhi-ncr", "CRM Software Development Company in Delhi NCR | GrowthSpare"),
        ("core:local-seo-shaheen", "SEO Company in Shaheen Bagh Okhla | GrowthSpare"),
        ("core:local-digital-south-delhi", "Digital Marketing Agency in South Delhi | GrowthSpare"),
    ]

    def _json_ld_graphs(self, html):
        scripts = re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', html, re.DOTALL
        )
        graphs = []
        for script in scripts:
            data = json.loads(script.replace("&quot;", '"'))
            if isinstance(data, dict) and "@graph" in data:
                graphs.extend(data["@graph"])
            elif isinstance(data, dict):
                graphs.append(data)
        return graphs

    def test_pages_return_200_with_unique_metadata(self):
        client = Client()
        seen_titles, seen_descriptions = set(), set()
        for url_name, expected_title in self.PAGES:
            with self.subTest(page=url_name):
                response = client.get(reverse(url_name))
                self.assertEqual(response.status_code, 200)
                html = response.content.decode()
                self.assertIn(f"<title>{expected_title}</title>", html)
                self.assertEqual(html.lower().count("<h1"), 1)
                self.assertIn('rel="canonical"', html)
                self.assertIn("https://growthspareitsolutions.com", html)
                m = re.search(r'<meta name="description" content="([^"]+)"', html)
                self.assertIsNotNone(m)
                seen_titles.add(expected_title)
                seen_descriptions.add(m.group(1))
        self.assertEqual(len(seen_titles), 4)
        self.assertEqual(len(seen_descriptions), 4)

    def test_pages_emit_valid_schema_graph(self):
        client = Client()
        for url_name, _ in self.PAGES:
            with self.subTest(page=url_name):
                html = client.get(reverse(url_name)).content.decode()
                types = [g.get("@type") for g in self._json_ld_graphs(html)]
                for required in ("ProfessionalService", "Service", "BreadcrumbList", "FAQPage"):
                    self.assertIn(required, types)
                self.assertIn("+91 9811579273", html)
                self.assertIn("D-50, Shaheen Bagh, Okhla", html)
                self.assertIn("tel:+919811579273", html)

    def test_pages_listed_in_sitemap_and_robots_allows(self):
        client = Client()
        sitemap = client.get("/sitemap.xml").content.decode()
        for slug in (
            "website-development-company-okhla-delhi",
            "crm-software-development-company-delhi-ncr",
            "seo-company-shaheen-bagh-okhla",
            "digital-marketing-agency-south-delhi",
        ):
            self.assertIn(slug, sitemap)
        robots = client.get("/robots.txt").content.decode()
        self.assertIn("Sitemap:", robots)
        self.assertIn("Disallow: /admin/", robots)


class ContactAntiSpamTestCase(TestCase):
    """Verifies contact-form rate limiting, duplicate protection, and budget options."""

    BLOCKED_MESSAGE = "Too many submissions from this contact information."

    def setUp(self):
        # Isolate per-test counters (test client shares IP; locmem cache otherwise
        # carries django-ratelimit + throttle counters across tests).
        cache.clear()
        self.client = Client()
        self.url = reverse("contact:contact")

    def _post_lead(self, name="Test User", email="user@example.com",
                   phone="+91 9811000001", budget="75k_1l",
                   service="web_dev", message="Need a business website."):
        return self.client.post(self.url, {
            "name": name,
            "email": email,
            "phone": phone,
            "company": "Test Co",
            "budget": budget,
            "service": service,
            "message": message,
        })

    def test_normal_submission_succeeds(self):
        response = self._post_lead()
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_rate_limit_blocks_fourth_submission_same_email(self):
        # Same email, distinct phones (avoids the duplicate rule) — the first
        # three are legitimate, the fourth trips the 3/hour identity limit.
        for i in range(3):
            response = self._post_lead(phone=f"+91 981100000{i}")
            self.assertEqual(response.status_code, 302)
        response = self._post_lead(phone="+91 9811000009")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.BLOCKED_MESSAGE)
        self.assertEqual(ContactMessage.objects.count(), 3)

    def test_blocked_submissions_create_no_record(self):
        for i in range(3):
            self.assertEqual(
                self._post_lead(email="repeat@example.com",
                                phone=f"+91 981100001{i}").status_code, 302
            )
        before = ContactMessage.objects.count()
        self.assertEqual(before, 3)
        response = self._post_lead(email="repeat@example.com",
                                   phone="+91 9811000099")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.BLOCKED_MESSAGE)
        self.assertEqual(ContactMessage.objects.count(), before)

    def test_duplicate_submission_rejected(self):
        self.assertEqual(self._post_lead().status_code, 302)
        # Same email + phone with a different message is still a duplicate.
        response = self._post_lead(message="Same person writing again.")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.BLOCKED_MESSAGE)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_duplicate_matches_phone_format_variants(self):
        self.assertEqual(self._post_lead(phone="+91 9811000001").status_code, 302)
        response = self._post_lead(phone="9811000001")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.BLOCKED_MESSAGE)
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_different_users_not_blocked(self):
        for i in range(3):
            response = self._post_lead(
                name=f"Person {i}",
                email=f"person{i}@example.com",
                phone=f"+91 981200000{i}",
            )
            self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 3)

    @override_settings(CONTACT_RATE_LIMIT_COUNT=100)
    def test_all_new_budget_options_accepted(self):
        for i, key in enumerate(
            ["30k_50k", "50k_75k", "75k_1l", "1l_1_5l", "1_5l_2l", "2l_plus"]
        ):
            # Reset per-test counters (outer 5/min IP ratelimit + throttle
            # state) so each iteration purely validates budget acceptance.
            cache.clear()
            response = self._post_lead(
                email=f"budget{i}@example.com",
                phone=f"+91 981300000{i}",
                budget=key,
            )
            self.assertEqual(response.status_code, 302, f"budget {key} rejected")
        self.assertEqual(ContactMessage.objects.count(), 6)

    def test_old_database_records_remain_readable(self):
        # Legacy budget keys predate the new choices; rows must stay readable.
        legacy = ContactMessage.objects.create(
            name="Legacy Lead",
            email="legacy@example.com",
            phone="+91 9814000000",
            company="Old Co",
            budget="1l_3l",
            service="web_dev",
            message="Old record.",
        )
        fetched = ContactMessage.objects.get(pk=legacy.pk)
        self.assertEqual(fetched.name, "Legacy Lead")
        # get_budget_display must not raise for values outside current choices.
        self.assertTrue(str(fetched.get_budget_display()))