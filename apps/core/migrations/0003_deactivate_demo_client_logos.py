# Generated manually for Django 6.0.6
"""
The homepage displays a "Trusted by growing businesses across India, Europe &
the Middle East" strip backed by ClientLogo records. All 6 existing records
("DataCore Systems", "Arvex Retail", "Nexora Logistics", "Velunex Textiles",
"Skyline Ventures", "Primeon Manufacturing") are demo/placeholder entries —
they have no uploaded logo, no website_url, and are the exact names the
model's own STATIC_PLACEHOLDER_LOGOS dict documents as "known demo clients".

Showing them under a specific, geographic trust claim misrepresents them as
real client relationships. This migration deactivates (is_active=False) only
these 6 specifically-named demo entries — HomeView already filters on
is_active=True, so the section will simply not render until genuine client
logos are added via the admin (no template change needed, and this in no
way prevents real logos from being added later).

Non-destructive: records are deactivated, not deleted, and re-activatable
via the admin. Idempotent — safe to re-run.
"""

from django.db import migrations

DEMO_CLIENT_NAMES = [
    "DataCore Systems",
    "Arvex Retail",
    "Nexora Logistics",
    "Velunex Textiles",
    "Skyline Ventures",
    "Primeon Manufacturing",
]


def deactivate_demo_clients(apps, schema_editor):
    ClientLogo = apps.get_model("core", "ClientLogo")
    ClientLogo.objects.filter(name__in=DEMO_CLIENT_NAMES).update(is_active=False)


def reactivate_demo_clients(apps, schema_editor):
    """Reverse migration — restores prior visibility if ever needed."""
    ClientLogo = apps.get_model("core", "ClientLogo")
    ClientLogo.objects.filter(name__in=DEMO_CLIENT_NAMES).update(is_active=True)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_clientlogo'),
    ]

    operations = [
        migrations.RunPython(deactivate_demo_clients, reactivate_demo_clients),
    ]
