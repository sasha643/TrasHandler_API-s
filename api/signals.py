from django.db.models.signals import post_save
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from .models import Notification, PickupRequest, UserToken, VendorLocation
from .tasks import send_notification_task, reassign_pickup_request, send_refreshed_token_notification
import redis
import geohash
import secrets

from django.dispatch import Signal


websocket_disconnected = Signal()

@receiver(post_save, sender=VendorLocation)
def generate_vendor_geohash(sender, instance, **kwargs):
    # Check if latitude and longitude are present
    if instance.latitude and instance.longitude:
        # Generate geohash using the latitude and longitude
        vendor_geohash = geohash.encode(instance.latitude, instance.longitude, precision=4)
        
        # Save the generated geohash into the instance
        VendorLocation.objects.filter(id=instance.id).update(vendor_geohash=vendor_geohash)

@receiver(post_save, sender=Notification)
def handle_notification_save(sender, instance, **kwargs):
    # Check if the notification has already been delivered
    if not instance.delivered:
        # If not delivered, send the notification
        send_notification_task.delay(instance.user.id, instance.message)
    #     # Mark the notification as read if it is relevant and not for reassignment
    # elif instance.relevant:
    #     if instance.recipient_type == 'vendor' and 'reassign' not in instance.message.lower():
    #         Notification.objects.filter(id=instance.id).update(sent=True)
    #     elif instance.recipient_type == 'customer' and 'reassign' not in instance.message.lower():
    #         Notification.objects.filter(id=instance.id).update(sent=True)

@receiver(post_save, sender=PickupRequest)
def schedule_reassignment(sender, instance, created, **kwargs):
    if created and instance.status == 'Request Sent':
        # Start the reassignment process immediately upon creation
        reassign_pickup_request.apply_async((instance.id,), countdown=60)
        
@receiver(post_save, sender=UserToken)
def trigger_token_refresh_notification(sender, instance, **kwargs):
    if kwargs.get('created', False) is False:  # Trigger only on updates, not creation
        user_id = instance.user.id
        access_token = instance.access_token
        send_refreshed_token_notification.delay(user_id, access_token)

