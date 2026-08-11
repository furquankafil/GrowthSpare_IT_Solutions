"""
Django base settings for GrowthSpare IT Solutions project.

Django 6.0 compatible base configuration.
Docker + Gunicorn + Nginx deployment ready.
"""

import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv


load_dotenv()


# ==============================================================================
# Paths
# ==============================================================================

BASE_DIR = Path(__file__).resolve().parent.parent.parent


# ==============================================================================
# Security
# ==============================================================================

SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "django-insecure-default-dev-secret-key"
)

DEBUG = os.getenv("DEBUG", "True") == "True"


ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv(
        "ALLOWED_HOSTS",
        "localhost,127.0.0.1"
    ).split(",")
    if host.strip()
]


# ==============================================================================
# Applications
# ==============================================================================

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]


THIRD_PARTY_APPS = [
    "corsheaders",
    "csp",
    "rest_framework",
    "rest_framework_simplejwt",
    "crispy_forms",
    "crispy_tailwind",
    "crispy_bootstrap5",
]


LOCAL_APPS = [
    "apps.accounts.apps.AccountsConfig",
    "apps.core.apps.CoreConfig",
    "apps.services.apps.ServicesConfig",
    "apps.portfolio.apps.PortfolioConfig",
    "apps.blog.apps.BlogConfig",
    "apps.contact.apps.ContactConfig",
    "apps.consultation.apps.ConsultationConfig",
    "apps.faq.apps.FaqConfig",
    "apps.testimonials.apps.TestimonialsConfig",
    "apps.dashboard.apps.DashboardConfig",
]


INSTALLED_APPS = (
    DJANGO_APPS
    + THIRD_PARTY_APPS
    + LOCAL_APPS
)


# ==============================================================================
# Middleware
# ==============================================================================

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",

    # Disabled manifest compression issue
    "whitenoise.middleware.WhiteNoiseMiddleware",

    # Must sit above CommonMiddleware for CORS_ALLOWED_ORIGINS to take effect
    "corsheaders.middleware.CorsMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "csp.middleware.CSPMiddleware",
]


# ==============================================================================
# Templates
# ==============================================================================

ROOT_URLCONF = "config.urls"


TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

        "APP_DIRS": True,

        "OPTIONS": {
            "context_processors": [

                "django.template.context_processors.debug",

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

                "apps.core.context_processors.company_branding",

            ],
        },
    },
]


WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"


# ==============================================================================
# Database
# ==============================================================================

import dj_database_url
import os

DATABASES = {
    "default": dj_database_url.parse(
        os.environ["DATABASE_URL"],
        conn_max_age=600,
    )
}


# ==============================================================================
# Authentication
# ==============================================================================

AUTH_USER_MODEL = "accounts.User"


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME":
        "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.MinimumLengthValidator",
        "OPTIONS": {
            "min_length": 8,
        },
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME":
        "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# ==============================================================================
# Internationalization
# ==============================================================================

LANGUAGE_CODE = "en-us"

TIME_ZONE = "Asia/Kolkata"

USE_I18N = True

USE_TZ = True


# ==============================================================================
# Static Files (FIXED)
# ==============================================================================

STATIC_URL = "/static/"

STATIC_ROOT = BASE_DIR / "staticfiles"


STATICFILES_DIRS = [
    BASE_DIR / "static"
]


# CompressedManifestStaticFilesStorage: gzip/brotli pre-compression + hashed,
# cache-busting filenames. Previously disabled due to a manifest error that
# was actually caused by invalid @import paths in main.css (now fixed) —
# re-enabled and verified working via `collectstatic`.

STORAGES = {

    "default": {
        "BACKEND":
        "django.core.files.storage.FileSystemStorage",
    },

    "staticfiles": {

        "BACKEND":
        "whitenoise.storage.CompressedManifestStaticFilesStorage",

    },

}


# ==============================================================================
# Media
# ==============================================================================

MEDIA_URL = "/media/"

MEDIA_ROOT = BASE_DIR / "mediafiles"


# ==============================================================================
# Default Primary Key
# ==============================================================================

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ==============================================================================
# Crispy Forms
# ==============================================================================

CRISPY_ALLOWED_TEMPLATE_PACKS = (
    "tailwind",
    "bootstrap5",
)

CRISPY_TEMPLATE_PACK = "tailwind"


# ==============================================================================
# REST Framework
# ==============================================================================

REST_FRAMEWORK = {

    "DEFAULT_AUTHENTICATION_CLASSES": (

        "rest_framework_simplejwt.authentication.JWTAuthentication",

        "django.contrib.auth.backends.ModelBackend",

    ),

    "DEFAULT_PERMISSION_CLASSES": (

        "rest_framework.permissions.IsAuthenticatedOrReadOnly",

    ),

}



# ==============================================================================
# JWT
# ==============================================================================

SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME":
        timedelta(minutes=15),

    "REFRESH_TOKEN_LIFETIME":
        timedelta(days=7),

    "ROTATE_REFRESH_TOKENS":
        True,

    "BLACKLIST_AFTER_ROTATION":
        True,

    "UPDATE_LAST_LOGIN":
        True,

    "ALGORITHM":
        "HS256",

    "SIGNING_KEY":
        SECRET_KEY,

    "AUTH_HEADER_TYPES":
        ("Bearer",),

}



# ==============================================================================
# Email
# ==============================================================================

EMAIL_BACKEND = (
    "django.core.mail.backends.smtp.EmailBackend"
)


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
    "growthspareitsolution@gmail.com"
)


EMAIL_HOST_PASSWORD = os.getenv(
    "EMAIL_HOST_PASSWORD",
    ""
)


EMAIL_USE_TLS = True


DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL",
    "GrowthSpare IT Solutions <growthspareitsolution@gmail.com>"
)


# ==============================================================================
# Canonical Site URL (env-configurable)
# The absolute canonical origin used for <link rel="canonical">, Open Graph
# og:url, absolute image URLs, and JSON-LD "url" fields. Defaults to the
# production domain so temporary deployment URLs (Render/Railway/Netlify
# subdomains) never leak into canonical or social-crawler output.
# ==============================================================================

SITE_URL = os.getenv(
    "SITE_URL",
    "https://growthspareitsolutions.com",
)


# ==============================================================================
# Office Location & Google Maps Embed (env-configurable)
# Lets the corporate office address / map pin be changed per-deployment
# (e.g. a staging environment or a future office move) purely via .env,
# without touching template or view code.
# ==============================================================================

OFFICIAL_LOCATION_ADDRESS = os.getenv(
    "OFFICIAL_LOCATION_ADDRESS",
    "D-50, Shaheen Bagh, Okhla, New Delhi \u2013 110025, India",
)

# Plain-text query used to center the embedded map — usually the same
# address without special punctuation, e.g. "D-50, Shaheen Bagh, Okhla,
# New Delhi 110025". Kept separate from OFFICIAL_LOCATION_ADDRESS since the
# display address may contain characters (like the en dash above) that
# don't need to be part of the map search query.
GOOGLE_MAPS_EMBED_QUERY = os.getenv(
    "GOOGLE_MAPS_EMBED_QUERY",
    "D-50, Shaheen Bagh, Okhla, New Delhi 110025",
)


# ==============================================================================
# Content Security Policy (django-csp 4.x)
# Allows exactly the external hosts referenced in templates/base.html —
# Tailwind Play CDN, Google Fonts, FontAwesome, AOS, Swiper, GSAP, Typed.js.
# ==============================================================================

CONTENT_SECURITY_POLICY = {
    "DIRECTIVES": {
        "default-src": ["'self'"],
        "script-src": [
            "'self'",
            "'unsafe-inline'",
            "https://cdn.tailwindcss.com",
            "https://unpkg.com",
            "https://cdnjs.cloudflare.com",
            "https://cdn.jsdelivr.net",
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",
            "https://fonts.googleapis.com",
            "https://cdnjs.cloudflare.com",
            "https://unpkg.com",
            "https://cdn.jsdelivr.net",
        ],
        "font-src": [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com",
        ],
        "img-src": ["'self'", "data:", "https:"],
        "connect-src": ["'self'"],
        # Without an explicit frame-src, browsers fall back to default-src
        # ('self'), which silently blocks the Google Maps <iframe> embed on
        # the contact page — this is why the map was not loading in
        # production even though the markup itself was correct.
        "frame-src": [
            "'self'",
            "https://www.google.com",
            "https://maps.google.com",
        ],
        "frame-ancestors": ["'self'"],
    },
}