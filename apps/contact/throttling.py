"""
Server-side anti-spam layer for the contact form.

Layered, mostly database-backed protections (work with any cache backend,
including a down Redis — the per-IP counter below is the only cache user and
fails open safely):

1. Client-IP extraction — trusted forwarded headers only, and only when the
   deployment is configured as proxied (TRUST_PROXY_HEADERS). Used for the
   per-IP counters and for the blocklist IP lookups.
2. Honeypot — a hidden field real users never fill; a value means bot.
3. Submission speed — a signed render timestamp proves the form existed for at
   least CONTACT_MIN_SUBMIT_SECONDS before POST (missing/forged = bot).
4. Blocklist — identifiers (email/phone/IP) a staff member explicitly blocked
   via the admin. Never added automatically from a single suspicious message.
5. Duplicate detection — the same identity pair, phone+company pair, or a long
   copy-pasted message inside CONTACT_DUPLICATE_WINDOW_SECONDS. The first repeat
   is flagged as Spam for admin review instead of entering the lead pipeline.
6. Rate limiting — more than CONTACT_RATE_LIMIT_COUNT submissions sharing an
   email or phone within CONTACT_RATE_LIMIT_WINDOW_SECONDS, or more than
   CONTACT_RATE_LIMIT_IP_COUNT from one client IP, are rejected outright.

All checks are server-side; nothing here trusts client input beyond validated,
normalized form data. Reasons and identifiers never appear in public responses.
"""

import hashlib
import ipaddress
import re
import time
from datetime import timedelta

from django.conf import settings
from django.core.cache import caches
from django.core import signing
from django.db.models import Q
from django.utils import timezone

from .models import AbuseBlock, ContactMessage

# Salt for the signed contact-form render timestamp (independent of the
# session/CSRF salts so one cannot be replayed as the other).
FORM_TIMESTAMP_SALT = "apps.contact.form_timestamp"

# Messages shorter than this are far too likely to collide legitimately
# (e.g. "Need a website?") to be treated as copy-paste spam on their own.
MIN_DUPLICATE_MESSAGE_CHARS = 40


def _valid_ip(raw):
    """Return a parsed ipaddress object for a clean single IP string, else None."""
    candidate = (raw or "").strip()
    if not candidate:
        return None
    try:
        return ipaddress.ip_address(candidate)
    except ValueError:
        return None


def get_client_ip(request):
    """
    Originating client IP for abuse controls.

    Production topology (verified for this deployment): browser -> Cloudflare
    -> Render ingress -> gunicorn, so REMOTE_ADDR alone is the shared proxy IP
    for every visitor. Forwarded headers are therefore consulted ONLY when
    TRUST_PROXY_HEADERS is enabled (production, mirroring the existing
    SECURE_PROXY_SSL_HEADER configuration for the same proxy chain); local
    development and tests ignore them entirely.

    Trust order:
      1. CF-Connecting-IP — set and overwritten by Cloudflare at the edge, so a
         visitor cannot forge it through the public site.
      2. X-Forwarded-For — proxies append to the right and never clear
         client-supplied values on the left, so the real client is the
         rightmost globally routable hop; private/reserved hops are internal
         proxy layers and are skipped.
      3. REMOTE_ADDR — direct-connection fallback.

    Never returns an empty string (django-ratelimit requires a usable value).
    """
    remote = (request.META.get("REMOTE_ADDR") or "").strip()

    if not getattr(settings, "TRUST_PROXY_HEADERS", False):
        return remote or "0.0.0.0"

    cloudflare_ip = _valid_ip(request.META.get("HTTP_CF_CONNECTING_IP", ""))
    if cloudflare_ip:
        return str(cloudflare_ip)

    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        for part in reversed(forwarded.split(",")):
            hop = _valid_ip(part)
            if hop is not None and hop.is_global:
                return str(hop)

    return remote or "0.0.0.0"


def normalize_email(email):
    """Lowercase + trim so Case@X.com and case@x.com match."""
    return (email or "").strip().lower()


def normalize_name(name):
    """Lowercase + collapse whitespace for stable comparisons."""
    return re.sub(r"\s+", " ", (name or "").strip()).lower()


def normalize_phone(phone):
    """
    Digits only, with Indian trunk/country prefixes folded so
    "+91 98115 79273", "09811579273" and "9811579273" all match.
    """
    digits = re.sub(r"\D", "", phone or "")
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    if len(digits) == 11 and digits.startswith("0"):
        return digits[1:]
    return digits


def normalize_message(message):
    """Lowercase + collapse all whitespace runs so formatting-only edits match."""
    return re.sub(r"\s+", " ", (message or "")).strip().lower()


def normalize_block_value(kind, value):
    """Canonical stored form for a blocklist entry of the given kind."""
    raw = (value or "").strip()
    if not raw:
        return ""
    if kind == AbuseBlock.KIND_EMAIL:
        return normalize_email(raw)
    if kind == AbuseBlock.KIND_PHONE:
        return normalize_phone(raw)
    if kind == AbuseBlock.KIND_IP:
        parsed = _valid_ip(raw)
        return str(parsed) if parsed else ""
    return ""


def contact_identity_hash(email, phone):
    """SHA-256 of the normalized identity — used for cache keys, never raw PII."""
    raw = f"{normalize_email(email)}|{normalize_phone(phone)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def make_form_timestamp(age_seconds=0):
    """
    Signed render timestamp embedded in the served form. `age_seconds` lets
    tests simulate a form that was loaded a while ago; the live view always
    issues age_seconds=0 (rendered right now).
    """
    issued_at = time.time() - max(float(age_seconds), 0.0)
    return signing.dumps({"t": issued_at}, salt=FORM_TIMESTAMP_SALT)


def honeypot_triggered(form):
    """True when the hidden honeypot field carried any value (bot-filled)."""
    return bool(str(form.cleaned_data.get("website", "") or "").strip())


def submission_too_fast(raw_timestamp):
    """
    True unless the POST proves a human pacing: the form must carry a valid,
    unexpired signed render timestamp issued at least
    CONTACT_MIN_SUBMIT_SECONDS ago. Missing, forged, expired or
    future-dated timestamps all count as too fast (automated clients strip or
    fail to reproduce the signature).
    """
    if not raw_timestamp:
        return True

    min_seconds = float(getattr(settings, "CONTACT_MIN_SUBMIT_SECONDS", 3))
    max_age = int(getattr(settings, "CONTACT_FORM_MAX_AGE_SECONDS", 604800))

    try:
        payload = signing.loads(raw_timestamp, salt=FORM_TIMESTAMP_SALT, max_age=max_age)
        issued_at = float(payload["t"])
    except (signing.BadSignature, KeyError, TypeError, ValueError):
        return True

    return (time.time() - issued_at) < min_seconds


def _recent_messages(since):
    return ContactMessage.objects.filter(created_at__gte=since)


def find_duplicate(email, phone, message="", company=""):
    """
    Most recent submission inside the duplicate window matching this one on ANY
    of the combination rules below; returns that ContactMessage or None.

    - normalized email AND normalized phone (same person re-submitting, in any
      formatting variant)
    - normalized phone AND normalized company (same contact changing email)
    - identical long message body (>= MIN_DUPLICATE_MESSAGE_CHARS after
      normalization) — copy-pasted blasts from rotating identities
    """
    email = normalize_email(email)
    phone = normalize_phone(phone)
    company = normalize_name(company)
    message = normalize_message(message)

    window = int(getattr(settings, "CONTACT_DUPLICATE_WINDOW_SECONDS", 86400))
    since = timezone.now() - timedelta(seconds=window)

    candidates = _recent_messages(since).order_by("-created_at").only(
        "id", "email", "phone", "company", "message", "status", "spam_reason"
    )

    for existing in candidates:
        if email and phone:
            if (
                normalize_email(existing.email) == email
                and normalize_phone(existing.phone) == phone
            ):
                return existing
        if phone and company:
            if (
                normalize_phone(existing.phone) == phone
                and normalize_name(existing.company) == company
            ):
                return existing
        if len(message) >= MIN_DUPLICATE_MESSAGE_CHARS:
            if normalize_message(existing.message) == message:
                return existing
    return None


def is_rate_limited(request, email, phone):
    """
    True when CONTACT_RATE_LIMIT_COUNT or more submissions sharing this email
    or phone exist in the rate window, or the per-IP cache counter exceeds
    CONTACT_RATE_LIMIT_IP_COUNT (deliberately higher so offices/NATs sharing one
    IP are not throttled by colleague volume). Cache failures fail open — the
    database-backed identity rules still apply.
    """
    limit = int(getattr(settings, "CONTACT_RATE_LIMIT_COUNT", 3))
    ip_limit = int(getattr(settings, "CONTACT_RATE_LIMIT_IP_COUNT", 10))
    window = int(getattr(settings, "CONTACT_RATE_LIMIT_WINDOW_SECONDS", 3600))
    since = timezone.now() - timedelta(seconds=window)

    email = normalize_email(email)
    phone = normalize_phone(phone)

    # One window query; email compared case-insensitively and phone after
    # normalization in Python so formatting variants (+91, spaces, dashes)
    # count as the same contact. Contact tables are small; this stays cheap.
    recent = _recent_messages(since).only("id", "email", "phone")
    db_count = sum(
        1
        for msg in recent
        if (msg.email or "").strip().lower() == email
        or normalize_phone(msg.phone) == phone
    )
    if db_count >= limit:
        return True

    ip = get_client_ip(request)
    if ip:
        try:
            cache = caches["default"]
            key = f"contact:rl:ip:{hashlib.sha256(ip.encode()).hexdigest()}"
            count = cache.get(key, 0) + 1
            # set() (not incr) so a missing key also gets the window timeout
            cache.set(key, count, timeout=window)
            if count > ip_limit:
                return True
        except Exception:
            pass
    return False


def is_blocked(email, phone, ip=""):
    """
    True when a staff member has blocked this email, phone, or client IP in the
    Abuse Block admin. Matching uses the same normalization as submission data.
    """
    checks = []

    normalized_email = normalize_email(email)
    if normalized_email:
        checks.append((AbuseBlock.KIND_EMAIL, normalized_email))

    normalized_phone = normalize_phone(phone)
    if normalized_phone:
        checks.append((AbuseBlock.KIND_PHONE, normalized_phone))

    if ip:
        parsed_ip = _valid_ip(ip)
        if parsed_ip:
            checks.append((AbuseBlock.KIND_IP, str(parsed_ip)))

    if not checks:
        return False

    query = Q()
    for kind, value in checks:
        query |= Q(kind=kind, value=value, is_active=True)
    return AbuseBlock.objects.filter(query).exists()
