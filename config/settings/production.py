"""
GrowthSpare IT Solutions - Production Settings

Production configuration:
- DEBUG disabled
- Docker + Gunicorn support
- PostgreSQL support
- Static files handling
- Security configuration
"""

from .base import *
import os


def _env_bool(key, default=False):
    """Parses common truthy env var string representations safely."""
    return os.getenv(key, str(default)).strip().lower() in ("true", "1", "yes", "on")


def _env_list(key, default):
    """Parses a comma-separated env var into a clean list, falling back to default."""
    raw = os.getenv(key, "")
    items = [item.strip() for item in raw.split(",") if item.strip()]
    return items or default


# ==============================================================================
# Production Core Settings
# ==============================================================================

DEBUG = True


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-change-this-secret-key"
)


# ==============================================================================
# Allowed Hosts
# ==============================================================================

ALLOWED_HOSTS = [
    "localhost",
    "127.0.0.1",
    "0.0.0.0",
    "web",
    "nginx",
    "growthspareitsolutions.com",
    "www.growthspareitsolutions.com",
    "growthspare-it-solutions.onrender.com",
]


# ==============================================================================
# Database
# ==============================================================================

DATABASE_URL = os.getenv("DATABASE_URL")


if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600
        )
    }


# ==============================================================================
# Static & Media Files
# ==============================================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "mediafiles"


# NOTE: Static file storage backend is configured once, in base.py's STORAGES
# dict (Django 4.2+/6.0 mechanism). The legacy STATICFILES_STORAGE setting
# previously duplicated here has been removed to avoid the two conflicting.


# ==============================================================================
# Security Headers
# ==============================================================================

SECURE_PROXY_SSL_HEADER = (
    "HTTP_X_FORWARDED_PROTO",
    "https",
)


SECURE_SSL_REDIRECT = _env_bool("SECURE_SSL_REDIRECT", default=True)


SESSION_COOKIE_SECURE = _env_bool("SESSION_COOKIE_SECURE", default=True)


CSRF_COOKIE_SECURE = _env_bool("CSRF_COOKIE_SECURE", default=True)


SECURE_HSTS_SECONDS = int(os.getenv("SECURE_HSTS_SECONDS", "31536000"))


SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)


SECURE_HSTS_PRELOAD = _env_bool("SECURE_HSTS_PRELOAD", default=True)


SECURE_CONTENT_TYPE_NOSNIFF = True

SECURE_REFERRER_POLICY = "same-origin"


# ==============================================================================
# CSRF Configuration
# ==============================================================================

CSRF_TRUSTED_ORIGINS = _env_list("CSRF_TRUSTED_ORIGINS", [
    "https://growthspareitsolutions.com",
    "https://www.growthspareitsolutions.com",
])


# ==============================================================================
# CORS
# ==============================================================================

CORS_ALLOWED_ORIGINS = _env_list("CORS_ALLOWED_ORIGINS", [
    "https://growthspareitsolutions.com",
    "https://www.growthspareitsolutions.com",
])


# ==============================================================================
# Redis Cache
# ==============================================================================

REDIS_URL = os.getenv(
    "REDIS_URL",
    "redis://redis:6379/1"
)

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "TIMEOUT": 300,
    }
}

SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default"


# ==============================================================================
# Email Configuration
# ==============================================================================

EMAIL_HOST = os.getenv(
    "EMAIL_HOST",
    "smtp.gmail.com"
)

EMAIL_PORT = int(
    os.getenv(
        "EMAIL_PORT",
        587
    )
)

EMAIL_HOST_USER = os.getenv(
    "EMAIL_HOST_USER",
    ""
)

EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    ""
)

EMAIL_USE_TLS = True


# ==============================================================================
# Logging
# ==============================================================================

LOGGING = {
    "version": 1,

    "disable_existing_loggers": False,

    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },

    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },

    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },

    "loggers": {
        # Surfaces unhandled 500s distinctly from general INFO noise
        "django.request": {
            "handlers": ["console"],
            "level": "ERROR",
            "propagate": False,
        },
        # Surfaces CSRF failures, disallowed hosts, suspicious operations
        "django.security": {
            "handlers": ["console"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}