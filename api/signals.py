import secrets
from .models import CustomerAuth, VendorAuth, PickupRequest
from django.db.models.signals import post_save
from django.dispatch import receiver
from .views import RejectAndReassignPickupRequestView
from rest_framework.test import APIRequestFactory

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

@receiver(post_save, sender=PickupRequest)
def auto_reassign_pickup_request(sender, instance, **kwargs):
    if instance.status == 'Rejected':
        # Temporarily disconnect the signal
        post_save.disconnect(auto_reassign_pickup_request, sender=PickupRequest)

        try:
            # Create a request factory
            factory = APIRequestFactory()
            request = factory.post('',{
                'vendor_id': instance.vendor.id,
                'pickup_request_id': instance.id,
            })

            # Instantiate the view and call the view's dispatch method
            view = RejectAndReassignPickupRequestView.as_view()
            response = view(request)

            # Optionally handle the response if needed
            if response.status_code == 200:
                # Success handling
                pass
            else:
                # Error handling
                pass
        finally:
            # Reconnect the signal
            post_save.connect(auto_reassign_pickup_request, sender=PickupRequest)