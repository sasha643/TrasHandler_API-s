import asyncio
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels.layers import get_channel_layer
from rest_framework.exceptions import AuthenticationFailed
from asgiref.sync import async_to_sync
from .models import CustomerAuth, VendorAuth, PickupRequest
import logging

# Configure logging
logger = logging.getLogger(__name__)

class PickupRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.customer_id = self.scope['url_route']['kwargs']['customer_id']
        self.authenticated_user = None
        self.notification_task = None
        logger.debug(f"WebSocket connected for customer_id: {self.customer_id}")
        await self.accept()

    async def receive(self, text_data):
        data = json.loads(text_data)
        if data.get('type') == 'authenticate':
            token = data.get('token').split()[1]  # Extract token
            try:
                self.authenticated_user = await self.authenticate(token)
                await self.send(json.dumps({'message': 'Authenticated successfully'}))
                await self.channel_layer.group_add(
                    f'customer_{self.customer_id}',
                    self.channel_name
                )
                # Start the continuous notification task
                self.notification_task = asyncio.create_task(self.continuous_notification_check())
                logger.debug(f"User authenticated and added to group for customer_id: {self.customer_id}")
            except AuthenticationFailed as e:
                await self.send(json.dumps({'error': str(e)}))
                await self.close()
                logger.warning(f"Authentication failed: {e}")
        else:
            if not self.authenticated_user:
                await self.send(json.dumps({'error': 'Authentication required'}))
                await self.close()
                logger.warning("Received message without authentication")

    async def disconnect(self, close_code):
        if self.authenticated_user:
            await self.channel_layer.group_discard(
                f'customer_{self.customer_id}',
                self.channel_name
            )
        if self.notification_task:
            self.notification_task.cancel()  # Cancel the notification task when disconnected
        logger.debug(f"WebSocket disconnected for customer_id: {self.customer_id}")

    @database_sync_to_async
    def authenticate(self, token):
        try:
            vendor_auth = VendorAuth.objects.get(token=token)
            return self.authenticate_vendor(vendor_auth)
        except VendorAuth.DoesNotExist:
            try:
                customer_auth = CustomerAuth.objects.get(token=token)
                return self.authenticate_customer(customer_auth)
            except CustomerAuth.DoesNotExist:
                raise AuthenticationFailed('Invalid token or user not found.')

    def authenticate_vendor(self, vendor_auth):
        return vendor_auth

    def authenticate_customer(self, customer_auth):
        return customer_auth

    @database_sync_to_async
    def get_pickup_request(self):
        return PickupRequest.objects.filter(customer_id=self.customer_id, status='Accepted', notification_sent=False).first()

    @database_sync_to_async
    def mark_notification_as_sent(self, pickup_request_id):
        pickup_request = PickupRequest.objects.get(id=pickup_request_id)
        pickup_request.notification_sent = True
        pickup_request.save()

    async def send_pickup_request_notification(self, pickup_request):
        if pickup_request:
            vendor_details = await self.get_vendor_details(pickup_request.vendor_id)
            await self.send(text_data=json.dumps({
                'pickup_request_id': pickup_request.id,
                'vendor_details': vendor_details
            }))
            logger.debug(f"Pickup request notification sent: {pickup_request.id}")
            await self.mark_notification_as_sent(pickup_request.id)

    async def continuous_notification_check(self):
        while True:
            pickup_request = await self.get_pickup_request()
            if pickup_request:
                await self.send_pickup_request_notification(pickup_request)
            await asyncio.sleep(0.5)

    @database_sync_to_async
    def get_vendor_details(self, vendor_id):
        try:
            vendor = VendorAuth.objects.get(id=vendor_id)
            return {'name': vendor.name, 'mobile_no': vendor.mobile_no}
        except VendorAuth.DoesNotExist:
            return {'name': 'Unknown', 'mobile_no': 'Unknown'}

    async def notify_pickup_request(self, event):
        pickup_request_id = event['pickup_request_id']
        vendor_details = event['vendor_details']
        await self.send(text_data=json.dumps({
            'pickup_request_id': pickup_request_id,
            'vendor_details': vendor_details
        }))
        logger.debug(f"Pickup request update notified: {pickup_request_id}")
