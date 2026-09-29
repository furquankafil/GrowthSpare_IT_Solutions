"""
Automated coverage for the multi-layer contact-form anti-spam system:

- page render carries the honeypot + signed render timestamp
- honeypot and submission-speed gates reject silently, record nothing
- blocklist (staff-created) rejects with the generic rejection message
- duplicate repeats are flagged Spam once, later repeats dropped
- per-IP and per-identity rate limiting reject without records
- Spam status admin workflow: filters, actions, block action, deletion
- staff dashboard pipeline metrics exclude spam rows
- trusted client-IP extraction honours TRUST_PROXY_HEADERS and anti-spoof rules
"""

import re
import time as stdlib_time
from unittest import mock

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import (
    Client,
    RequestFactory,
    SimpleTestCase,
    TestCase,
    override_settings,
)
from django.urls import reverse

from apps.contact.models import AbuseBlock, ContactMessage
from apps.contact.throttling import get_client_ip, make_form_timestamp

User = get_user_model()

# Verbatim user-facing strings — the entire anti-spam UX contract: humans get
# readable generic copy, automated clients never learn which rule fired.
GENERIC_TOAST = "An error occurred during submission"
RATE_LIMIT_MESSAGE = "Too many submissions from this contact information."
REJECTION_MESSAGE = "We could not process this submission right now."

# Never send real SMTP traffic from test submissions.
LOCMEM_EMAIL = "django.core.mail.backends.locmem.EmailBackend"

# Longer than throttling.MIN_DUPLICATE_MESSAGE_CHARS, so an identical body from
# a rotating identity trips the copy-paste duplicate rule on its own.
COPY_PASTE_MESSAGE = (
    "Please rebuild our legacy ERP portal with role based dashboards, "
    "bulk CSV exports and full audit logging."
)


class ContactFormTestMixin:
    """Isolated cache/client plus a payload builder that passes the speed gate."""

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.url = reverse("contact:contact")

    def _payload(self, **overrides):
        data = {
            "name": "Legit Visitor",
            "email": "visitor@example.com",
            "phone": "+91 9811100001",
            "company": "Legit Co",
            "budget": "50k_75k",
            "service": "web_dev",
            "message": "Need a business website.",
            # Submitted 60 seconds after render — passes the human-speed gate.
            "form_timestamp": make_form_timestamp(age_seconds=60),
        }
        data.update(overrides)
        return data


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactFormRenderingTests(ContactFormTestMixin, TestCase):
    """The served page must carry both anti-spam inputs with sane markup."""

    def test_form_renders_honeypot_and_signed_timestamp(self):
        html = self.client.get(self.url).content.decode()

        honeypot = re.search(r"<input[^>]*name=\"website\"[^>]*>", html)
        self.assertIsNotNone(honeypot, "honeypot input missing from contact page")
        hp_tag = honeypot.group(0)
        self.assertIn('type="text"', hp_tag)
        self.assertIn('aria-hidden="true"', hp_tag)
        self.assertIn('tabindex="-1"', hp_tag)
        self.assertIn("left:-9999px", hp_tag)
        # Off-screen, not display:none: scrapers still see it, humans never do.
        self.assertNotIn("display:none", hp_tag)
        self.assertNotIn("display: none", hp_tag)

        stamp = re.search(r"<input[^>]*name=\"form_timestamp\"[^>]*>", html)
        self.assertIsNotNone(stamp, "form_timestamp input missing from contact page")
        value = re.search(r'value="([^"]*)"', stamp.group(0))
        self.assertIsNotNone(value)
        self.assertTrue(value.group(1), "render timestamp issued empty")


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactHoneypotTests(ContactFormTestMixin, TestCase):
    """Bot-filled honeypot: silent rejection, no record, no rule disclosure."""

    def test_filled_honeypot_rejected_without_record(self):
        response = self.client.post(self.url, self._payload(website="http://spam.example"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        html = response.content.decode()
        self.assertIn(GENERIC_TOAST, html)
        # Silent rejection: no blocklist, rate-limit or speed-rule wording.
        self.assertNotIn(REJECTION_MESSAGE, html)
        self.assertNotIn(RATE_LIMIT_MESSAGE, html)

    def test_empty_honeypot_with_paced_timestamp_accepted(self):
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactSpeedCheckTests(ContactFormTestMixin, TestCase):
    """Signed render timestamp must prove realistic human pacing."""

    def test_immediate_submission_rejected(self):
        response = self.client.post(
            self.url, self._payload(form_timestamp=make_form_timestamp(age_seconds=0))
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn(GENERIC_TOAST, response.content.decode())

    def test_missing_timestamp_rejected(self):
        payload = self._payload()
        payload.pop("form_timestamp")
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_forged_timestamp_rejected(self):
        response = self.client.post(
            self.url, self._payload(form_timestamp="forged.not-a-real-signature")
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_expired_render_timestamp_rejected(self):
        # A token actually signed CONTACT_FORM_MAX_AGE_SECONDS + 60 ago (the
        # scenario of a tab left open for a week) fails the max-age check.
        offset = int(getattr(settings, "CONTACT_FORM_MAX_AGE_SECONDS", 604800)) + 60
        with mock.patch.object(
            stdlib_time, "time", return_value=stdlib_time.time() - offset
        ):
            stale = make_form_timestamp()
        response = self.client.post(self.url, self._payload(form_timestamp=stale))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_human_paced_submission_accepted(self):
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)
        lead = ContactMessage.objects.get()
        self.assertEqual(lead.status, ContactMessage.STATUS_NEW)
        self.assertIsNotNone(lead.ip_address)


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactDuplicateFlaggingTests(ContactFormTestMixin, TestCase):
    """First repeat is kept flagged as Spam; later repeats are dropped."""

    def test_first_repeat_flagged_spam_not_dropped_silently(self):
        self.assertEqual(self.client.post(self.url, self._payload()).status_code, 302)
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, 200)
        self.assertIn(RATE_LIMIT_MESSAGE, response.content.decode())
        self.assertEqual(ContactMessage.objects.count(), 2)

        spam = ContactMessage.objects.get(status=ContactMessage.STATUS_SPAM)
        self.assertEqual(spam.spam_reason, ContactMessage.REASON_DUPLICATE)
        self.assertFalse(spam.is_processed)
        self.assertEqual(spam.email, "visitor@example.com")
        self.assertTrue(
            ContactMessage.objects.filter(status=ContactMessage.STATUS_NEW).exists()
        )

    def test_later_repeats_do_not_grow_the_table(self):
        self.assertEqual(self.client.post(self.url, self._payload()).status_code, 302)
        self.assertEqual(self.client.post(self.url, self._payload()).status_code, 200)
        response = self.client.post(self.url, self._payload())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 2)

    def test_copy_pasted_long_message_from_new_identity_flagged(self):
        self.assertEqual(
            self.client.post(self.url, self._payload(message=COPY_PASTE_MESSAGE)).status_code,
            302,
        )
        response = self.client.post(
            self.url,
            self._payload(
                email="rotating@example.com",
                phone="+91 9811100077",
                message=COPY_PASTE_MESSAGE,
            ),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(RATE_LIMIT_MESSAGE, response.content.decode())
        self.assertEqual(ContactMessage.objects.count(), 2)
        spam = ContactMessage.objects.get(status=ContactMessage.STATUS_SPAM)
        self.assertEqual(spam.spam_reason, ContactMessage.REASON_DUPLICATE)
        self.assertEqual(spam.email, "rotating@example.com")

    def test_distinct_legitimate_submissions_not_flagged(self):
        for i in range(3):
            response = self.client.post(
                self.url,
                self._payload(
                    email=f"lead{i}@example.com",
                    phone=f"+91 981110001{i}",
                    message=(
                        f"I need a full CRM rebuild for business unit {i} "
                        "with offline sync and reporting."
                    ),
                ),
            )
            self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 3)
        self.assertFalse(
            ContactMessage.objects.filter(status=ContactMessage.STATUS_SPAM).exists()
        )


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactRateLimitTests(ContactFormTestMixin, TestCase):
    """django-ratelimit 5/min decorator + the per-IP hourly cache counter."""

    def test_sixth_post_blocked_by_per_minute_ip_limit(self):
        for i in range(5):
            response = self.client.post(
                self.url,
                self._payload(
                    email=f"rush{i}@example.com",
                    phone=f"+91 981110002{i}",
                ),
            )
            self.assertEqual(response.status_code, 302)
        response = self.client.post(
            self.url,
            self._payload(email="rush5@example.com", phone="+91 9811100025"),
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ContactMessage.objects.count(), 5)

    @override_settings(CONTACT_RATE_LIMIT_IP_COUNT=2)
    def test_per_ip_hour_counter_blocks_repeated_volume(self):
        # Distinct identities (identity limits untouched): the per-IP counter
        # alone must stop the third submission inside the hour.
        for i in range(2):
            response = self.client.post(
                self.url,
                self._payload(
                    email=f"nat{i}@example.com",
                    phone=f"+91 981110003{i}",
                ),
            )
            self.assertEqual(response.status_code, 302)
        response = self.client.post(
            self.url,
            self._payload(email="nat2@example.com", phone="+91 9811100039"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn(RATE_LIMIT_MESSAGE, response.content.decode())
        self.assertEqual(ContactMessage.objects.count(), 2)


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class ContactBlocklistTests(ContactFormTestMixin, TestCase):
    """Staff-created Abuse Block entries reject submissions without records."""

    def test_blocked_email_rejected_without_record(self):
        AbuseBlock.block_identifier(
            AbuseBlock.KIND_EMAIL, "banned@example.com", reason="manual review"
        )
        response = self.client.post(self.url, self._payload(email="banned@example.com"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        html = response.content.decode()
        self.assertIn(REJECTION_MESSAGE, html)
        # Generic rejection only — the rate-limit wording stays reserved for
        # rate/duplicate paths, and no rule detail leaks.
        self.assertNotIn(RATE_LIMIT_MESSAGE, html)

    def test_blocked_phone_matches_format_variants(self):
        AbuseBlock.block_identifier(AbuseBlock.KIND_PHONE, "+91 9876543210")
        response = self.client.post(
            self.url,
            self._payload(email="fresh-identity@example.com", phone="09876543210"),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn(REJECTION_MESSAGE, response.content.decode())

    def test_deactivated_block_no_longer_matches(self):
        block = AbuseBlock.block_identifier(
            AbuseBlock.KIND_EMAIL, "banned@example.com"
        )
        block.is_active = False
        block.save()
        response = self.client.post(self.url, self._payload(email="banned@example.com"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 1)

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_blocked_ip_rejected_via_trusted_cloudflare_header(self):
        AbuseBlock.block_identifier(AbuseBlock.KIND_IP, "93.184.216.34")
        response = self.client.post(
            self.url,
            self._payload(email="ip-blocked@example.com"),
            HTTP_CF_CONNECTING_IP="93.184.216.34",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn(REJECTION_MESSAGE, response.content.decode())


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class SpamStatusAdminTests(TestCase):
    """Spam status admin workflow: save mirror, actions, filters, block, delete."""

    def setUp(self):
        cache.clear()
        self.admin_user = User.objects.create_superuser(
            username="spam_admin",
            email="spam.admin@example.com",
            password="panel-pass-123456",
            role="ADMIN",
        )
        self.admin_client = Client()
        self.admin_client.force_login(self.admin_user)
        self.changelist_url = reverse("admin:contact_contactmessage_changelist")
        self.lead = ContactMessage.objects.create(
            name="Fresh Lead",
            email="fresh.lead@example.com",
            phone="+91 9811200000",
            company="Fresh Co",
            budget="75k_1l",
            service="web_dev",
            message="We need a new company website.",
            ip_address="93.184.216.50",
        )

    def test_status_is_authoritative_and_mirrors_legacy_flag(self):
        self.assertEqual(self.lead.status, ContactMessage.STATUS_NEW)
        self.assertFalse(self.lead.is_processed)

        self.lead.status = ContactMessage.STATUS_PROCESSED
        self.lead.save()
        refetched = ContactMessage.objects.get(pk=self.lead.pk)
        self.assertTrue(refetched.is_processed)

        self.lead.status = ContactMessage.STATUS_SPAM
        self.lead.save()
        refetched = ContactMessage.objects.get(pk=self.lead.pk)
        self.assertFalse(refetched.is_processed)

    def test_mark_as_spam_and_unmark_actions(self):
        response = self.admin_client.post(
            self.changelist_url,
            {
                "action": "mark_as_spam",
                "_selected_action": [str(self.lead.pk)],
                "index": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        refetched = ContactMessage.objects.get(pk=self.lead.pk)
        self.assertEqual(refetched.status, ContactMessage.STATUS_SPAM)
        self.assertEqual(refetched.spam_reason, ContactMessage.REASON_MANUAL)
        self.assertFalse(refetched.is_processed)

        response = self.admin_client.post(
            self.changelist_url,
            {
                "action": "unmark_as_spam",
                "_selected_action": [str(self.lead.pk)],
                "index": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        refetched = ContactMessage.objects.get(pk=self.lead.pk)
        self.assertEqual(refetched.status, ContactMessage.STATUS_NEW)
        self.assertEqual(refetched.spam_reason, "")
        self.assertFalse(refetched.is_processed)

    def test_changelist_status_filter_and_search(self):
        ContactMessage.objects.create(
            name="Spammy Lead",
            email="spammy@example.com",
            phone="+91 9876500001",
            company="Spam Co",
            budget="30k_50k",
            service="other",
            message="Bulk outreach copy.",
            status=ContactMessage.STATUS_SPAM,
            spam_reason=ContactMessage.REASON_MANUAL,
        )
        response = self.admin_client.get(
            self.changelist_url, {"status__exact": ContactMessage.STATUS_SPAM}
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spammy Lead")
        self.assertNotContains(response, "Fresh Lead")

        response = self.admin_client.get(self.changelist_url, {"q": "Spammy"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Spammy Lead")

        # The status filter itself is offered in the sidebar.
        response = self.admin_client.get(self.changelist_url)
        self.assertContains(response, "status__exact")

    def test_delete_flow_removes_spam_record(self):
        ContactMessage.objects.filter(pk=self.lead.pk).update(
            status=ContactMessage.STATUS_SPAM,
            spam_reason=ContactMessage.REASON_MANUAL,
        )
        delete_url = reverse(
            "admin:contact_contactmessage_delete", args=[self.lead.pk]
        )
        confirm = self.admin_client.get(delete_url)
        self.assertEqual(confirm.status_code, 200)
        response = self.admin_client.post(delete_url, {"post": "yes"})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(ContactMessage.objects.count(), 0)

    def test_block_action_creates_entries_and_blocks_public_form(self):
        response = self.admin_client.post(
            self.changelist_url,
            {
                "action": "block_selected_identities",
                "_selected_action": [str(self.lead.pk)],
                "index": "0",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(AbuseBlock.objects.filter(is_active=True).count(), 3)
        self.assertTrue(
            AbuseBlock.objects.filter(
                kind=AbuseBlock.KIND_EMAIL, value="fresh.lead@example.com"
            ).exists()
        )
        self.assertTrue(
            AbuseBlock.objects.filter(
                kind=AbuseBlock.KIND_PHONE, value="9811200000"
            ).exists()
        )
        self.assertTrue(
            AbuseBlock.objects.filter(
                kind=AbuseBlock.KIND_IP, value="93.184.216.50"
            ).exists()
        )

        # The public form now rejects that email outright, recording nothing.
        cache.clear()
        public = Client()
        payload = {
            "name": "Blocked Visitor",
            "email": "fresh.lead@example.com",
            "phone": "+91 9811100001",
            "company": "Legit Co",
            "budget": "50k_75k",
            "service": "web_dev",
            "message": "Need a business website.",
            "form_timestamp": make_form_timestamp(age_seconds=60),
        }
        response = public.post(reverse("contact:contact"), payload)
        self.assertEqual(response.status_code, 200)
        self.assertIn(REJECTION_MESSAGE, response.content.decode())
        self.assertEqual(ContactMessage.objects.count(), 1)

    def test_abuse_block_admin_registered(self):
        response = self.admin_client.get(
            reverse("admin:contact_abuseblock_changelist")
        )
        self.assertEqual(response.status_code, 200)


@override_settings(EMAIL_BACKEND=LOCMEM_EMAIL)
class DashboardSpamExclusionTests(TestCase):
    """Staff pipeline metrics must never count or list spam rows."""

    def setUp(self):
        cache.clear()
        self.manager = User.objects.create_user(
            username="ops_manager",
            email="ops@example.com",
            password="manager-pass-123456",
            role="MANAGER",
        )
        self.client.force_login(self.manager)
        ContactMessage.objects.create(
            name="Fresh Lead",
            email="fresh@example.com",
            phone="+91 9811300000",
            budget="50k_75k",
            service="web_dev",
            message="Legit inquiry from a real prospect.",
        )
        ContactMessage.objects.create(
            name="Spammy Lead",
            email="spam@example.com",
            phone="+91 9811300001",
            budget="50k_75k",
            service="other",
            message="Copy-pasted promotional content.",
            status=ContactMessage.STATUS_SPAM,
            spam_reason=ContactMessage.REASON_DUPLICATE,
        )

    def test_spam_excluded_from_staff_pipeline_metrics(self):
        response = self.client.get(reverse("dashboard:index"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["total_leads"], 1)
        recent_names = [lead.name for lead in response.context["recent_leads"]]
        self.assertIn("Fresh Lead", recent_names)
        self.assertNotIn("Spammy Lead", recent_names)


class ClientIPExtractionTests(SimpleTestCase):
    """Trusted forwarded-header handling for per-IP counters and IP blocking."""

    def setUp(self):
        self.factory = RequestFactory()

    @override_settings(TRUST_PROXY_HEADERS=False)
    def test_untrusted_environment_ignores_forwarded_headers(self):
        request = self.factory.get(
            "/",
            HTTP_X_FORWARDED_FOR="93.184.216.34",
            HTTP_CF_CONNECTING_IP="93.184.216.35",
        )
        self.assertEqual(get_client_ip(request), "127.0.0.1")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_cloudflare_header_wins(self):
        request = self.factory.get(
            "/",
            HTTP_CF_CONNECTING_IP="93.184.216.34",
            HTTP_X_FORWARDED_FOR="1.2.3.4",
        )
        self.assertEqual(get_client_ip(request), "93.184.216.34")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_spoofed_leftmost_forwarded_hop_ignored(self):
        request = self.factory.get(
            "/", HTTP_X_FORWARDED_FOR="1.2.3.4, 93.184.216.34"
        )
        self.assertEqual(get_client_ip(request), "93.184.216.34")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_private_proxy_hops_skipped(self):
        request = self.factory.get(
            "/", HTTP_X_FORWARDED_FOR="93.184.216.34, 10.0.0.7"
        )
        self.assertEqual(get_client_ip(request), "93.184.216.34")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_falls_back_to_remote_addr(self):
        request = self.factory.get("/")
        self.assertEqual(get_client_ip(request), "127.0.0.1")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_malformed_cloudflare_header_falls_through(self):
        request = self.factory.get("/", HTTP_CF_CONNECTING_IP="not-an-ip")
        self.assertEqual(get_client_ip(request), "127.0.0.1")

    @override_settings(TRUST_PROXY_HEADERS=True)
    def test_every_trusted_path_returns_usable_value(self):
        # django-ratelimit refuses an empty key; none of the branches may
        # return an empty string.
        for meta in (
            {},
            {"HTTP_X_FORWARDED_FOR": "   "},
            {"HTTP_X_FORWARDED_FOR": "10.0.0.1, 192.168.1.1"},
            {"HTTP_CF_CONNECTING_IP": ""},
        ):
            request = self.factory.get("/", **meta)
            self.assertTrue(get_client_ip(request))
