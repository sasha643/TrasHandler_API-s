# Generated by Django 4.0.10 on 2024-05-11 14:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='VendorAuth',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254, unique=True)),
                ('mobile_no', models.CharField(max_length=15)),
            ],
        ),
        migrations.AlterField(
            model_name='customerauth',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True),
        ),
    ]
