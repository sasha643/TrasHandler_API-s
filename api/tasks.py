from datetime import timedelta
from django.utils import timezone
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


@shared_task
def schedule_pickup_requests():
    now = timezone.now()
    current_time = now.time()

    # Define time slots for scheduling
    morning_slot_start = timezone.datetime.combine(now.date(), timezone.datetime.strptime('11:00 AM', '%I:%M %p').time())
    morning_slot_end = timezone.datetime.combine(now.date(), timezone.datetime.strptime('12:00 PM', '%I:%M %p').time())
    
    evening_slot_start = timezone.datetime.combine(now.date(), timezone.datetime.strptime('5:00 PM', '%I:%M %p').time())
    evening_slot_end = timezone.datetime.combine(now.date(), timezone.datetime.strptime('6:00 PM', '%I:%M %p').time())

    # Define time periods for workflow logic
    pre_morning_slot_start = morning_slot_start - timedelta(minutes=30)
    pre_evening_slot_start = evening_slot_start - timedelta(minutes=30)

    # Handle Next Day Morning Slot Allocation
    if current_time >= evening_slot_end.time() or current_time < morning_slot_start.time():
        next_day_morning_slot_start = morning_slot_start + timedelta(days=1)
        next_day_morning_slot_end = morning_slot_end + timedelta(days=1)

        # Allocate requests accepted after 6:00 PM to next day morning slot
        pickup_requests = PickupRequest.objects.filter(
            status='Accepted',
            accepted_time__gte=timezone.datetime.combine(now.date(), timezone.datetime.strptime('6:00 PM', '%I:%M %p').time()),
            accepted_time__lt=next_day_morning_slot_start
        )

        for request in pickup_requests:
            # Notify customer about next day collection slot
            message = f"Your pickup request is scheduled for the next day's Morning Slot (11:00 AM - 12:00 PM)."
            send_notification_task.delay(request.customer.id, message)

    # Morning Slot Workflow (11:00 AM - 12:00 PM)
    elif pre_morning_slot_start.time() <= current_time < morning_slot_end.time():
        pickup_requests = PickupRequest.objects.filter(
            status='Accepted',
            accepted_time__gte=pre_morning_slot_start,
            accepted_time__lt=morning_slot_end
        )

        for request in pickup_requests:
            if current_time < morning_slot_start.time():
                # Allocate requests accepted before 11:00 AM to the Evening Slot
                message = f"Your pickup request is scheduled for the Evening Slot (5:00 PM - 6:00 PM)."
                send_notification_task.delay(request.customer.id, message)
            else:
                # Active collection period (11:00 AM - 12:00 PM)
                vendor_id = assign_vendor_task.delay(request.customer.id, request.latitude, request.longitude).get()
                if vendor_id:
                    vendor_location = (request.vendor.latitude, request.vendor.longitude)
                    customer_location = (request.latitude, request.longitude)
                    distance = haversine(vendor_location[0], vendor_location[1], customer_location[0], customer_location[1])
                    
                    if distance <= 1.0:  # If within 1 km radius
                        # Notify vendor and customer about active collection
                        customer_message = f"Your pickup request will be collected in the Morning Slot (11:00 AM - 12:00 PM)."
                        send_notification_task.delay(request.customer.id, customer_message)
                        
                        vendor_message = f"Pickup request at {customer_location} is within 1 km of your route."
                        send_notification_task.delay(vendor_id, vendor_message)

    # Evening Slot Workflow (5:00 PM - 6:00 PM)
    elif pre_evening_slot_start.time() <= current_time < evening_slot_end.time():
        pickup_requests = PickupRequest.objects.filter(
            status='Accepted',
            accepted_time__gte=pre_evening_slot_start,
            accepted_time__lt=evening_slot_end
        )

        for request in pickup_requests:
            if current_time < evening_slot_start.time():
                # Allocate requests accepted before 5:00 PM to the Evening Slot
                message = f"Your pickup request is scheduled for the Evening Slot (5:00 PM - 6:00 PM)."
                send_notification_task.delay(request.customer.id, message)
            else:
                # Active collection period (5:00 PM - 6:00 PM)
                vendor_id = assign_vendor_task.delay(request.customer.id, request.latitude, request.longitude).get()
                if vendor_id:
                    vendor_location = (request.vendor.latitude, request.vendor.longitude)
                    customer_location = (request.latitude, request.longitude)
                    distance = haversine(vendor_location[0], vendor_location[1], customer_location[0], customer_location[1])
                    
                    if distance <= 1.0:  # If within 1 km radius
                        # Notify vendor and customer about active collection
                        customer_message = f"Your pickup request will be collected in the Evening Slot (5:00 PM - 6:00 PM)."
                        send_notification_task.delay(request.customer.id, customer_message)
                        
                        vendor_message = f"Pickup request at {customer_location} is within 1 km of your route."
                        send_notification_task.delay(vendor_id, vendor_message)
