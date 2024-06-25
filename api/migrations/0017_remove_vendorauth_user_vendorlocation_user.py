# Generated by Django 4.0.10 on 2024-06-02 16:59

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0016_vendorlocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendorauth',
            name='user',
        ),
        migrations.AddField(
            model_name='vendorlocation',
            name='user',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]