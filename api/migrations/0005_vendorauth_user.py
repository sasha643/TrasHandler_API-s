# Generated by Django 4.0.10 on 2024-06-02 14:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0004_vendorlocation'),
    ]

    operations = [
    migrations.AddField(
        model_name='vendorauth',
        name='user',
        field=models.OneToOneField(null=True, blank=True, on_delete=models.CASCADE, to='auth.User'),
    ),
]
