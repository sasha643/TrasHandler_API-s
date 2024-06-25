# Generated by Django 4.0.10 on 2024-06-02 17:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0017_remove_vendorauth_user_vendorlocation_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendorlocation',
            name='user',
        ),
        migrations.AlterField(
            model_name='vendorlocation',
            name='vendor',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]