"""
Django development settings for GrowthSpare IT Solutions project.

Extends base configurations with active debugging tools, local caching,
and insecure local overrides for continuous verification.
"""

from .base import *

DEBUG = True

# Ensure localhost is explicitly configured for host header validations
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]

# local cache engine pointing to in-memory store
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "growthspare-local-cache",
    }
}

# Insecure local development security flag bypasses
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False
SECURE_HSTS_PRELOAD = False

# Fallback development email configuration
if not EMAIL_HOST_PASSWORD:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# CORS and CSRF local trusted bypass origins
CORS_ALLOW_ALL_ORIGINS = True
CSRF_TRUSTED_ORIGINS = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]