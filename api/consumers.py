import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import PickupRequest, VendorAuth, CustomerAuth, Notification, VendorLocation
from .functions import haversine
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from api.tasks import assign_vendor_task


class PickupRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'pickup_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        result = await self.create_pickup_request(data)
        await self.send(text_data=json.dumps(result))

    @database_sync_to_async
    def create_pickup_request(self, data):
        latitude = data['latitude']
        longitude = data['longitude']

        try:
            customer = CustomerAuth.objects.get(id=self.user.id)
        except CustomerAuth.DoesNotExist:
            return {"error": "Customer profile not found"}

        task_result = assign_vendor_task.delay(self.user.id, latitude, longitude)
        nearest_vendor_id = task_result.get()


        if nearest_vendor_id:
            nearest_vendor = VendorAuth.objects.get(id=nearest_vendor_id)
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                vendor=nearest_vendor,
                status='Request Sent'
            )

            # Notify the nearest vendor
            message = {
                "message": f"Pickup request sent by {pickup_request.customer.name}, his number is {pickup_request.customer.mobile_no}",
                "latitude": pickup_request.latitude,
                "longitude": pickup_request.longitude,
            }
            Notification.objects.create(
                user=nearest_vendor, 
                message=json.dumps(message), 
                relevant=True,
                recipient_type='vendor'
            )

            return {
                "message": "Pickup request created and assigned to the nearest active vendor",
                "pickup_request": {
                    "id": pickup_request.id,
                    "customer": pickup_request.customer.id,
                    "latitude": pickup_request.latitude,
                    "longitude": pickup_request.longitude,
                    "vendor": pickup_request.vendor.id,
                    "status": pickup_request.status
                }
            }
        else:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                status='No Active Vendors Available'
            )
            return {"error": "No active vendors found"}


class RejectAndReassignPickupRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'rejectandreassign_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        result = await self.reject_and_reassign_pickup_request(data)
        await self.send(text_data=json.dumps(result))

    @database_sync_to_async
    def reject_and_reassign_pickup_request(self, data):
        pickup_request_id = data.get('pickup_request_id')

        if not pickup_request_id:
            return {'error': 'pickup_request_id is required'}

        try:
            vendor = VendorAuth.objects.get(id=self.user.id)
        except VendorAuth.DoesNotExist:
            return {"error": "Vendor profile not found"}

        try:
            pickup_request = PickupRequest.objects.get(id=pickup_request_id, vendor=vendor)
            customer = pickup_request.customer
        except PickupRequest.DoesNotExist:
            return {"error": "Pickup request not found for the provided ID and vendor"}

        # Mark the current vendor as having rejected the request
        pickup_request.status = 'Rejected'
        pickup_request.rejected_vendors.add(vendor)
        pickup_request.save()

        # Notify the customer of reassigned pickup request
        Notification.objects.create(
            user=customer, 
            message="Pickup request has been reassigned to another vendor", 
            relevant=False,
            recipient_type='customer'
        )

        # Find the next nearest active vendor who has not rejected the request
        excluded_vendor_ids = list(pickup_request.rejected_vendors.values_list('id', flat=True))
        task_result = assign_vendor_task.delay(customer.id, pickup_request.latitude, pickup_request.longitude, excluded_vendor_ids)
        
        nearest_vendor_id = task_result.get()
        
        if nearest_vendor_id:
            nearest_vendor = VendorAuth.objects.get(id=nearest_vendor_id)
            pickup_request.vendor = nearest_vendor
            pickup_request.status = 'Request Sent'
            pickup_request.save()

            # Notify the new nearest vendor
            Notification.objects.create(
                user=nearest_vendor, 
                message=json.dumps({
                    "message": f"New pickup request from {pickup_request.customer.name}, Mobile No: {pickup_request.customer.mobile_no}",
                    "latitude": pickup_request.latitude,
                    "longitude": pickup_request.longitude
                }), 
                relevant=True,
                recipient_type='vendor'
            )

            return {
                "message": "Pickup request reassigned to the next nearest active vendor",
                "pickup_request": {
                    "id": pickup_request.id,
                    "customer": pickup_request.customer.id,
                    "latitude": pickup_request.latitude,
                    "longitude": pickup_request.longitude,
                    "vendor": pickup_request.vendor.id,
                    "status": pickup_request.status
                }
            }
        else:
            return {"error": "No other active vendors available"}


class UpdatePickupRequestStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'updatepickup_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        result = await self.update_pickup_request_status(data)
        await self.send(text_data=json.dumps(result))

    @database_sync_to_async
    def update_pickup_request_status(self, data):
        pickup_request_id = data.get('pickup_request_id')
        new_status = data.get('status')

        if not pickup_request_id or not new_status:
            return {'error': 'pickup_request_id and status are required'}

        try:
            vendor = VendorAuth.objects.get(id=self.user.id)
            pickup_request = PickupRequest.objects.get(id=pickup_request_id, vendor=vendor)
            customer = pickup_request.customer

            pickup_request.status = new_status
            pickup_request.save()

            if new_status == 'Accepted':
                message = {
                    "message": f"Your pickup request has been accepted by {vendor.name}",
                    "latitude": pickup_request.latitude,
                    "longitude": pickup_request.longitude,
                }
                Notification.objects.create(
                    user=customer, 
                    message=json.dumps(message), 
                    relevant=True,
                    recipient_type='customer'
                )

            return {
                "message": "Status updated successfully",
                "pickup_request_id": pickup_request.id,
                "status": new_status
            }
        except VendorAuth.DoesNotExist:
            return {'error': 'Vendor profile not found'}
        except PickupRequest.DoesNotExist:
            return {'error': 'Pickup request not found for the provided ID and vendor'}


class CustomerRejectPickupRequestConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'customerReject_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        result = await self.customer_reject_pickup_request(data)
        await self.send(text_data=json.dumps(result))

    @database_sync_to_async
    def customer_reject_pickup_request(self, data):
        pickup_request_id = data.get('pickup_request_id')
        remarks = data.get('remarks')

        try:
            customer = CustomerAuth.objects.get(id=self.user.id)
        except CustomerAuth.DoesNotExist:
            return {"error": "Customer profile not found"}

        try:
            pickup_request = PickupRequest.objects.get(id=pickup_request_id, customer=customer)
            vendor = pickup_request.vendor
        except PickupRequest.DoesNotExist:
            return {"error": "Pickup request not found for the provided ID and customer"}

        if pickup_request.status != 'Accepted':
            return {"error": "This pickup request is not currently accepted by any vendor"}

        pickup_request.status = 'Rejected'
        pickup_request.remarks = remarks
        pickup_request.save()

        # Notify the vendor of reassigned pickup request
        message = f"Pickup request has been cancelled by the  customer"
        Notification.objects.create(
            user=vendor, 
            message=message, 
            relevant=False,
            recipient_type='vendor'
        )

        return {"message": "Pickup request rejected successfully", "pickup_request_id": pickup_request_id}

    
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user.is_authenticated:
            self.group_name = f'Notifications_{self.user.id}'
            await self.accept()
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            print(f"User {self.user.id} connected to group {self.group_name} on channel {self.channel_name}")

    async def disconnect(self, close_code):
        if self.user.is_authenticated:
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            print(f"User {self.user.id} disconnected from group {self.group_name} on channel {self.channel_name}")

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        print(f"Sending notification to user {self.user.id} on channel {self.channel_name}")
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
