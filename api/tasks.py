import asyncio
from datetime import timedelta
import traceback
import websockets
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
import time
import jwt
from jwt import InvalidTokenError, ExpiredSignatureError
from django.conf import settings
from django.contrib.auth import get_user_model
from api.models import UserToken




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
def send_refreshed_token_notification(user_id, access_token):
    try:
        logger.info(f"Sending refreshed token to user_id: {user_id}")
        channel_layer = get_channel_layer()
        group_name = f'Token_{user_id}'
        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                'type': 'send_token',
                'access_token': access_token,
            }
        )
        logger.info(f"Refreshed token sent successfully to {group_name}.")
    except Exception as e:
        logger.error(f"Error sending refreshed token: {e}")
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
    access_token_lifetime = timedelta(minutes=10)  # From your SIMPLE_JWT config
    expiration_threshold = timedelta(minutes=5)  # Refresh tokens 5 minutes before they expire

    tokens = UserToken.objects.all()
    now = timezone.now()  # Get current time with timezone awareness

    for token_entry in tokens:
        # Calculate the token's age
        token_age = now - token_entry.token_created_at
        time_until_expiration = access_token_lifetime - token_age

        # Check if the token is close to expiration (less than 5 minutes left)
        if time_until_expiration <= expiration_threshold:
            # Refresh token using the refresh token endpoint
            refresh_url = 'http://3.108.52.92:8000//auth/token/refresh/'
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
                    token_entry.token_created_at = now  # Update the time to now
                    token_entry.save()

                    logger.info(f"Successfully refreshed tokens for {token_entry.user.name}")
                else:
                    logger.error(f"Failed to refresh tokens for {token_entry.user.name}: {response_data.get('detail')}")
            except Exception as e:
                logger.error(f"Error occurred while refreshing tokens for {token_entry.user.name}: {str(e)}")
        else:
            logger.info(f"Token for {token_entry.user.name} is not close to expiration, no refresh needed.")

@shared_task
def reassign_pickup_request(pickup_id):
    try:
        pickup = PickupRequest.objects.get(id=pickup_id)
        
        if pickup.status != 'Request Sent':
            return

        # If the current vendor's 60-second window has passed
        if timezone.now() >= pickup.created_at + timedelta(seconds=60):
            current_vendor = pickup.vendor

            if current_vendor:
                # Automatically reject the request for the current vendor
                pickup.rejected_vendors.add(current_vendor)
                Notification.objects.create(
                    user=current_vendor, 
                    message="The pickup request has been automatically reassigned as no action was taken.", 
                    relevant=False,
                    recipient_type='vendor'
                )

            # Find the next nearest vendor who has not rejected the request
            excluded_vendor_ids = list(pickup.rejected_vendors.values_list('id', flat=True))
            next_vendor = find_next_nearest_vendor(pickup, excluded_vendor_ids)

            if next_vendor:
                # Reassign to the next nearest vendor
                pickup.vendor = next_vendor
                pickup.status = 'Request Sent'
                pickup.created_at = timezone.now()  # Reset the timer for the new vendor
                pickup.save()

                # Notify the new nearest vendor
                Notification.objects.create(
                    user=next_vendor, 
                    message=json.dumps({
                        "message": f"New pickup request from {pickup.customer.name}, Mobile No: {pickup.customer.mobile_no}",
                        "latitude": pickup.latitude,
                        "longitude": pickup.longitude
                    }), 
                    relevant=True,
                    recipient_type='vendor'
                )

                # Restart the countdown with a 1-second delay
                reassign_pickup_request.apply_async((pickup.id,), countdown=60)  # 60 seconds plus 1 second delay
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

        else:
            # If the vendor has not rejected and 60 seconds have not passed, reschedule the check
            time_elapsed = timezone.now() - pickup.created_at
            remaining_time = 60 - time_elapsed.total_seconds()
            reassign_pickup_request.apply_async((pickup.id,), countdown=max(int(remaining_time), 1))

    except PickupRequest.DoesNotExist:
        # Handle the case where the pickup request was deleted
        pass


def find_next_nearest_vendor(pickup, excluded_vendor_ids):
    """
    Helper function to find the next nearest vendor.
    """
    nearest_vendor = None
    nearest_distance = None

    for location in VendorLocation.objects.filter(is_active=True).exclude(vendor__id__in=excluded_vendor_ids):
        distance = haversine(pickup.latitude, pickup.longitude, location.latitude, location.longitude)
        if nearest_distance is None or distance < nearest_distance:
            nearest_distance = distance
            nearest_vendor = location.vendor
    
    return nearest_vendor


def get_user_token(user):
    try:
        return UserToken.objects.get(user=user)
    except UserToken.DoesNotExist:
        return None

# @shared_task()
# def fetch_access_token_for_user(provided_token):
#     user = get_user_from_token(provided_token)
#     if not user:
#         return {'error': 'Invalid or expired token provided.'}

#     token_data = get_user_token(user)
#     if token_data:
#         ws_url = f"ws://localhost:8000/ws/get_access_token/?token={token_data.access_token}"
    
#         try:
#             # Establish a WebSocket connection
#             ws = websocket.create_connection(ws_url)
            
#             # Wait for the response (assuming your consumer sends the tokens immediately)
#             ws.send(json.dumps({}))
#             response = ws.recv()
#             ws.close()

#             # Parse the JSON response
#             tokens_data = json.loads(response)
#             print(f"Access Token: {tokens_data['access_token']}")
#         except Exception as e:
#             print(f"Failed to fetch tokens for user {user}: {str(e)}")
#             traceback.print_exc()

#     else:
#         return {'error': 'No token data available for user.'}

# def get_user_from_token(token):
#     try:
#         decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
#         user_id = decoded.get('user_id')
#         return User.objects.get(id=user_id)
#     except (InvalidTokenError, User.DoesNotExist):
#         return None

# def get_user_token(user):
#     try:
#         return UserToken.objects.get(user=user)
#     except UserToken.DoesNotExist:
#         return None

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
