# Generated by Django 4.0.10 on 2024-06-02 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0011_vendorauth_user_vendorlocation'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vendorauth',
            name='user',
        ),
    ]
