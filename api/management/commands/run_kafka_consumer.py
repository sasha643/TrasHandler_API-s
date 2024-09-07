from django.core.management.base import BaseCommand
from kafka import KafkaConsumer
import json
from api.models import VendorLocation, VendorAuth, PickupRequest
from api.serializers import VendorLocationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Run Kafka consumer for processing messages'

    def handle(self, *args, **kwargs):
        consumer = KafkaConsumer(
            'vendor-location-topic',
            bootstrap_servers='localhost:9092',
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        def handle_message(message):
            action = message.get('action')
            vendor_id = message.get('vendor_id')
            data = message.get('data')

            # Log the incoming message data
            self.stdout.write(f"Received message: {json.dumps(message, indent=4)}")

            try:
                vendor = VendorAuth.objects.get(id=vendor_id)
            except VendorAuth.DoesNotExist:
                self.stdout.write(f"Vendor with id {vendor_id} not found")
                return

            try:
                pickup_request = PickupRequest.objects.get(vendor=vendor, status='Accepted')
                customer = pickup_request.customer
            except PickupRequest.DoesNotExist:
                self.stdout.write(f"No assigned pickup request found for vendor {vendor_id}")
                return

            if action == 'create':
                serializer = VendorLocationSerializer(data=data)
                if serializer.is_valid():
                    if data.get('is_active'):
                        VendorLocation.objects.filter(vendor=vendor, is_active=True).update(is_active=False)
                    location = serializer.save(vendor=vendor)
                    self.stdout.write(f"Location created for vendor {vendor_id}")
                    self.stdout.write(json.dumps(VendorLocationSerializer(location).data, indent=4))
                    send_location_to_customer(customer.id, location)
                else:
                    self.stdout.write(str(serializer.errors))

            elif action == 'update':
                try:
                    # Find the active location for the vendor
                    location = VendorLocation.objects.get(vendor=vendor, is_active=True)
                except VendorLocation.DoesNotExist:
                    self.stdout.write(f"Active location not found for vendor {vendor_id}")
                    return

                serializer = VendorLocationSerializer(location, data=data, partial=True)
                if serializer.is_valid():
                    if data.get('is_active'):
                        VendorLocation.objects.filter(vendor=vendor, is_active=True).update(is_active=False)
                    updated_location = serializer.save(vendor=vendor)
                    self.stdout.write(f"Location updated for vendor {vendor_id}")
                    self.stdout.write(json.dumps(VendorLocationSerializer(updated_location).data, indent=4))
                    send_location_to_customer(customer.id, updated_location)
                else:
                    self.stdout.write(str(serializer.errors))

        def send_location_to_customer(customer_id, location):
            channel_layer = get_channel_layer()
            group_name = f'customer_location_{customer_id}'
            location_data = {
                'latitude': location.latitude,
                'longitude': location.longitude,
            }
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'location.update',
                    'location_data': location_data,
                }
            )
            self.stdout.write(f"Sent location data to customer {customer_id}")

        self.stdout.write('Starting Kafka consumer...')
        for message in consumer:
            handle_message(message.value)



