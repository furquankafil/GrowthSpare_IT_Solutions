# Data migration: map the legacy is_processed boolean onto the new tri-state
# status so no historical lead loses its state. Runs after 0003 added the
# column; purely an UPDATE, safe to re-run (idempotent by construction).

from django.db import migrations


def backfill_status(apps, schema_editor):
    ContactMessage = apps.get_model("contact", "ContactMessage")
    # Legacy "sales reviewed" rows become Processed; everything else already
    # defaults to New. Spam did not exist historically, so nothing maps to it.
    ContactMessage.objects.filter(is_processed=True).update(status="processed")


def unbackfill_status(apps, schema_editor):
    # Reverse is a no-op: the boolean mirror was rewritten by ContactMessage.save()
    # going forward, and dropping newer states would destroy data.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("contact", "0003_contactmessage_ip_address_contactmessage_spam_reason_and_more"),
    ]

    operations = [
        migrations.RunPython(backfill_status, unbackfill_status),
    ]
