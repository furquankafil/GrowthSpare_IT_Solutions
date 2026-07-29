# Generated manually for Django 6.0.6

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0002_alter_service_pricing_estimate_alter_service_title'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='use_cases',
            field=models.TextField(blank=True, help_text='Real-world scenarios/industries this service applies to. Enter one item per line.'),
        ),
        migrations.AddField(
            model_name='service',
            name='why_choose_us',
            field=models.TextField(blank=True, help_text='Reasons to choose GrowthSpare for this specific service. Enter one item per line.'),
        ),
        migrations.AddField(
            model_name='service',
            name='cta_headline',
            field=models.CharField(blank=True, help_text="Optional custom call-to-action headline for this service's detail page banner.", max_length=200),
        ),
        migrations.AddField(
            model_name='service',
            name='cta_subtext',
            field=models.CharField(blank=True, help_text='Optional supporting line shown under the call-to-action headline.', max_length=255),
        ),
    ]
