# Generated manually for Django 6.0.6
"""
The testimonial cards already render a dedicated "Sample Review" badge
(see templates/core/home.html and templates/testimonials/testimonial_list.html),
so having "[Sample Review] ", "[Example Testimonial] ", or "[Demo Feedback] "
repeated as literal text inside the quote itself is redundant and reads as
unpolished rather than transparent. This migration strips those prefixes
from the review text, leaving the honest labelling to the template badge
where it belongs. Idempotent — safe to re-run.
"""

from django.db import migrations

PREFIXES = ["[Sample Review] ", "[Example Testimonial] ", "[Demo Feedback] "]


def strip_prefixes(apps, schema_editor):
    Testimonial = apps.get_model("testimonials", "Testimonial")
    for testimonial in Testimonial.objects.all():
        review = testimonial.review
        changed = False
        for prefix in PREFIXES:
            if review.startswith(prefix):
                review = review[len(prefix):]
                changed = True
                break
        if changed:
            testimonial.review = review
            testimonial.save(update_fields=["review"])


def noop_reverse(apps, schema_editor):
    """Text-cleanup-only migration — nothing structural to reverse."""
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('testimonials', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(strip_prefixes, noop_reverse),
    ]
