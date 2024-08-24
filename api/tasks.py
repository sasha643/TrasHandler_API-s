from datetime import timedelta
import websocket
from django.utils import timezone
import logging
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction, connection
from .models import CustomerAuth, VendorLocation, UserToken, PickupRequest, Notification
from .functions import haversine
import requests
import json



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
def refresh_tokens():
    now = timezone.now()
    expiration_threshold = timedelta(minutes=5)  # Refresh tokens minutes before they expire

    tokens = UserToken.objects.all()
    for token_entry in tokens:
        # Check if the token is near expiration
        token_age = now - token_entry.token_created_at
        if token_age >= expiration_threshold:
            # Refresh token using the refresh token endpoint
            refresh_url = 'http://127.0.0.1:8000/auth/token/refresh/'
            payload = {
                'refresh': token_entry.refresh_token
            }
            try:
                response = requests.post(refresh_url, data=payload)
                response_data = response.json()

                if response.status_code == 200:
                    new_access_token = response_data.get('access')
                    new_refresh_token = response_data.get('refresh')
                    
                    # Update the tokens in the database
                    token_entry.access_token = new_access_token
                    token_entry.refresh_token = new_refresh_token
                    token_entry.token_created_at = now
                    token_entry.save()

                    logger.info(f"Refreshed tokens for {token_entry.user.name}")
                else:
                    logger.info(f"Failed to refresh token for {token_entry.user.name}: {response_data.get('detail')}")
            except Exception as e:
                logger.info(f"Error occurred while refreshing token for {token_entry.user.name}: {str(e)}")
        logger.info(f"token age less than expiration threshhold")

@shared_task()
def reassign_pickup_requests():
    one_minute_ago = timezone.now() - timedelta(minutes=1)
    pending_pickups = PickupRequest.objects.filter(status='Request Sent', created_at__lte=one_minute_ago)
    

    for pickup in pending_pickups:
        current_vendor = pickup.vendor
        
        # Automatically reject the request for the current vendor
        if current_vendor:
            pickup.rejected_vendors.add(current_vendor)
            Notification.objects.create(
                user=current_vendor, 
                message="The pickup request has been automatically reassigned as no action was taken.", 
                relevant=False,
                recipient_type='vendor'
            )

        # Find the next nearest active vendor who has not rejected the request
        excluded_vendor_ids = list(pickup.rejected_vendors.values_list('id', flat=True))
        
        # Calculate distances and find the nearest vendor
        nearest_vendor = None
        nearest_distance = None

        for location in VendorLocation.objects.filter(is_active=True).exclude(vendor__id__in=excluded_vendor_ids):
            distance = haversine(pickup.latitude, pickup.longitude, location.latitude, location.longitude)
            if nearest_distance is None or distance < nearest_distance:
                nearest_distance = distance
                nearest_vendor = location.vendor

        if nearest_vendor:
            # Reassign to the next nearest vendor
            pickup.vendor = nearest_vendor
            pickup.status = 'Request Sent'
            pickup.save()
            

            # Notify the new nearest vendor
            Notification.objects.create(
                user=nearest_vendor, 
                message=json.dumps({
                    "message": f"New pickup request from {pickup.customer.name}, Mobile No: {pickup.customer.mobile_no}",
                    "latitude": pickup.latitude,
                    "longitude": pickup.longitude
                }), 
                relevant=True,
                recipient_type='vendor'
            )
        else:
            # Notify the customer that no other active vendors are available
            Notification.objects.create(
                user=pickup.customer, 
                message="No active vendors are available to fulfill your pickup request at the moment.", 
                relevant=True,
                recipient_type='customer'
            )
            pickup.status = 'No Active Vendors Available'
            pickup.save()
            
@shared_task
def fetch_tokens_for_users():
    users = UserToken.objects.all()
    for user_token in users:
        ws_url = f"ws://localhost:8000/ws/get_access_token/?token={user_token.access_token}"
        try:
            # Connect to the WebSocket
            ws = websocket.create_connection(ws_url)
            ws.send(json.dumps({}))
            response = ws.recv()
            ws.close()

            # Parse the JSON response
            tokens_data = json.loads(response)
            print(f"Access Token for {user_token.user}: {tokens_data['access_token']}")
           
        except Exception as e:
            print(f"Failed to fetch tokens for user {user_token.user}: {str(e)}")
# @shared_task
# def schedule_pickup_requests():
#     now = timezone.now()
#     current_time = now.time()

#     # Define time slots for scheduling
#     morning_slot_start = timezone.datetime.combine(now.date(), timezone.datetime.strptime('11:00 AM', '%I:%M %p').time())
#     morning_slot_end = timezone.datetime.combine(now.date(), timezone.datetime.strptime('12:00 PM', '%I:%M %p').time())
    
#     evening_slot_start = timezone.datetime.combine(now.date(), timezone.datetime.strptime('5:00 PM', '%I:%M %p').time())
#     evening_slot_end = timezone.datetime.combine(now.date(), timezone.datetime.strptime('6:00 PM', '%I:%M %p').time())

#     # Define time periods for workflow logic
#     pre_morning_slot_start = morning_slot_start - timedelta(minutes=30)
#     pre_evening_slot_start = evening_slot_start - timedelta(minutes=30)

#     # Handle Next Day Morning Slot Allocation
#     if current_time >= evening_slot_end.time() or current_time < morning_slot_start.time():
#         next_day_morning_slot_start = morning_slot_start + timedelta(days=1)
#         next_day_morning_slot_end = morning_slot_end + timedelta(days=1)

#         # Allocate requests accepted after 6:00 PM to next day morning slot
#         pickup_requests = PickupRequest.objects.filter(
#             status='Accepted',
#             accepted_time__gte=timezone.datetime.combine(now.date(), timezone.datetime.strptime('6:00 PM', '%I:%M %p').time()),
#             accepted_time__lt=next_day_morning_slot_start
#         )

#         for request in pickup_requests:
#             # Notify customer about next day collection slot
#             message = f"Your pickup request is scheduled for the next day's Morning Slot (11:00 AM - 12:00 PM)."
#             send_notification_task.delay(request.customer.id, message)

#     # Morning Slot Workflow (11:00 AM - 12:00 PM)
#     elif pre_morning_slot_start.time() <= current_time < morning_slot_end.time():
#         pickup_requests = PickupRequest.objects.filter(
#             status='Accepted',
#             accepted_time__gte=pre_morning_slot_start,
#             accepted_time__lt=morning_slot_end
#         )

#         for request in pickup_requests:
#             if current_time < morning_slot_start.time():
#                 # Allocate requests accepted before 11:00 AM to the Evening Slot
#                 message = f"Your pickup request is scheduled for the Evening Slot (5:00 PM - 6:00 PM)."
#                 send_notification_task.delay(request.customer.id, message)
#             else:
#                 # Active collection period (11:00 AM - 12:00 PM)
#                 vendor_id = assign_vendor_task.delay(request.customer.id, request.latitude, request.longitude).get()
#                 if vendor_id:
#                     vendor_location = (request.vendor.latitude, request.vendor.longitude)
#                     customer_location = (request.latitude, request.longitude)
#                     distance = haversine(vendor_location[0], vendor_location[1], customer_location[0], customer_location[1])
                    
#                     if distance <= 1.0:  # If within 1 km radius
#                         # Notify vendor and customer about active collection
#                         customer_message = f"Your pickup request will be collected in the Morning Slot (11:00 AM - 12:00 PM)."
#                         send_notification_task.delay(request.customer.id, customer_message)
                        
#                         vendor_message = f"Pickup request at {customer_location} is within 1 km of your route."
#                         send_notification_task.delay(vendor_id, vendor_message)

#     # Evening Slot Workflow (5:00 PM - 6:00 PM)
#     elif pre_evening_slot_start.time() <= current_time < evening_slot_end.time():
#         pickup_requests = PickupRequest.objects.filter(
#             status='Accepted',
#             accepted_time__gte=pre_evening_slot_start,
#             accepted_time__lt=evening_slot_end
#         )

#         for request in pickup_requests:
#             if current_time < evening_slot_start.time():
#                 # Allocate requests accepted before 5:00 PM to the Evening Slot
#                 message = f"Your pickup request is scheduled for the Evening Slot (5:00 PM - 6:00 PM)."
#                 send_notification_task.delay(request.customer.id, message)
#             else:
#                 # Active collection period (5:00 PM - 6:00 PM)
#                 vendor_id = assign_vendor_task.delay(request.customer.id, request.latitude, request.longitude).get()
#                 if vendor_id:
#                     vendor_location = (request.vendor.latitude, request.vendor.longitude)
#                     customer_location = (request.latitude, request.longitude)
#                     distance = haversine(vendor_location[0], vendor_location[1], customer_location[0], customer_location[1])
                    
#                     if distance <= 1.0:  # If within 1 km radius
#                         # Notify vendor and customer about active collection
#                         customer_message = f"Your pickup request will be collected in the Evening Slot (5:00 PM - 6:00 PM)."
#                         send_notification_task.delay(request.customer.id, customer_message)
                        
#                         vendor_message = f"Pickup request at {customer_location} is within 1 km of your route."
#                         send_notification_task.delay(vendor_id, vendor_message)


    # 'schedule-pickup-requests': {
    #     'task': 'api.tasks.schedule_pickup_requests',
    #     'schedule': crontab(minute='*', hour='*'),  # Runs every hour
    # },