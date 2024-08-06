import logging
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction, connection
from .models import CustomerAuth, VendorLocation, PickupRequest, Notification
from .functions import haversine

logger = logging.getLogger(__name__)

@shared_task
def send_notification_task(user_id, message):
    try:
        logger.info(f"Sending notification to user_id: {user_id} with message: {message}")
        channel_layer = get_channel_layer()
        group_name = f'Notifications_{user_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_notification',
                'message': message,
            }
        )
        logger.info(f"Notification sent successfully to {group_name}.")
    except Exception as e:
        logger.error(f"Error sending notification: {e}")

@shared_task
def assign_vendor_task(customer_id, latitude, longitude, excluded_vendor_ids=[]):
    try:
        customer = CustomerAuth.objects.get(id=customer_id)
    except CustomerAuth.DoesNotExist:
        return {"error": "Customer profile not found"}

    active_vendors = VendorLocation.objects.exclude(vendor_id__in=excluded_vendor_ids).filter(is_active=True)
    min_distance = float('inf')
    nearest_vendor = None

    for vendor in active_vendors:
        distance = haversine(float(latitude), float(longitude), vendor.latitude, vendor.longitude)
        if distance < min_distance:
            min_distance = distance
            nearest_vendor = vendor

    if nearest_vendor:
        return nearest_vendor.vendor.id
    else:
        return None

