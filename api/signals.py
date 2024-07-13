import secrets
from .models import CustomerAuth, VendorAuth
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=CustomerAuth)
def generate_customer_token(sender, instance, created, **kwargs):
    if created and not instance.token:
        instance.token = secrets.token_urlsafe(32)
        instance.save()

@receiver(post_save, sender=VendorAuth)
def generate_vendor_token(sender, instance, created, **kwargs):
    if created and not instance.token:
        instance.token = secrets.token_urlsafe(32)
        instance.save()