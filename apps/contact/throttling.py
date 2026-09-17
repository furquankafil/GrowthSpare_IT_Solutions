"""
Server-side anti-spam throttling for the contact form.

Two complementary, database-backed protections (work with any cache backend,
including a down Redis — the per-IP counter below is the only cache user and
fails open safely):

1. Duplicate protection — the same normalized email + normalized phone seen
   within CONTACT_DUPLICATE_WINDOW_SECONDS is rejected without creating a
   new ContactMessage record.
2. Rate limiting — more than CONTACT_RATE_LIMIT_COUNT submissions sharing an
   email or phone within CONTACT_RATE_LIMIT_WINDOW_SECONDS are rejected.

A best-effort per-IP counter (Django cache, hashed key — no raw PII in cache
keys) adds protection against identity rotation. All checks are server-side;
nothing here trusts client input beyond validated, normalized form data.
"""

import hashlib
import ipaddress
import re
from datetime import timedelta

from django.conf import settings
from django.core.cache import caches
from django.utils import timezone

from .models import ContactMessage


def get_client_ip(request):
    """Best-effort client IP: first valid X-Forwarded-For hop, else REMOTE_ADDR."""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        for part in forwarded.split(","):
            candidate = part.strip()
            try:
                ipaddress.ip_address(candidate)
                return candidate
            except ValueError:
                continue
    return request.META.get("REMOTE_ADDR", "")


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


def contact_identity_hash(email, phone):
    """SHA-256 of the normalized identity — used for cache keys, never raw PII."""
    raw = f"{normalize_email(email)}|{normalize_phone(phone)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _recent_messages(since):
    return ContactMessage.objects.filter(created_at__gte=since)


def is_duplicate_submission(email, phone):
    """
    True when the same normalized email + normalized phone already submitted
    within the duplicate window. Email is matched in the DB (case-insensitive);
    phone formatting variants are compared in Python on that small subset so
    "+91-..." and plain digits count as the same contact.
    """
    email = normalize_email(email)
    phone = normalize_phone(phone)
    if not email or not phone:
        return False
    window = int(getattr(settings, "CONTACT_DUPLICATE_WINDOW_SECONDS", 86400))
    since = timezone.now() - timedelta(seconds=window)
    candidates = _recent_messages(since).filter(email__iexact=email).only(
        "id", "email", "phone"
    )
    return any(normalize_phone(msg.phone) == phone for msg in candidates)


def is_rate_limited(request, email, phone):
    """
    True when CONTACT_RATE_LIMIT_COUNT or more submissions sharing this email
    or phone exist in the rate window, or the best-effort per-IP cache counter
    exceeds the same limit. Cache failures fail open (DB rules still apply).
    """
    limit = int(getattr(settings, "CONTACT_RATE_LIMIT_COUNT", 3))
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
            if count > limit:
                return True
        except Exception:
            pass
    return False


def check_submission_allowed(request, email, phone):
    """
    Combined gate used by ContactView BEFORE saving.
    Returns (allowed: bool, reason: "duplicate" | "rate_limited" | None).
    """
    if is_duplicate_submission(email, phone):
        return False, "duplicate"
    if is_rate_limited(request, email, phone):
        return False, "rate_limited"
    return True, None
