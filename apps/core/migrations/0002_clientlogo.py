# Generated manually for the ClientLogo model (homepage "Trusted by" logos).

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ClientLogo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Client/partner company name. Used as image alt text and as the source for the fallback initials badge.', max_length=100)),
                ('logo', models.ImageField(blank=True, help_text='Company logo (PNG/SVG/JPG, transparent background recommended). Leave empty to display an automatic initials badge instead.', null=True, upload_to='clients/logos/')),
                ('website_url', models.URLField(blank=True, help_text="Optional link to the client's website when the logo is clicked.")),
                ('order', models.PositiveIntegerField(default=0, help_text='Ascending sort order priority.')),
                ('is_active', models.BooleanField(default=True, help_text='Controls whether this logo is displayed on the public homepage.')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Client Logo',
                'verbose_name_plural': 'Client Logos',
                'ordering': ['order', 'name'],
            },
        ),
    ]
