from django.core.management.base import BaseCommand
from confluent_kafka import Consumer, KafkaError
import json
from api.models import VendorLocation, VendorAuth, PickupRequest
from api.serializers import VendorLocationSerializer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

class Command(BaseCommand):
    help = 'Run Kafka consumer for processing messages'

    def handle(self, *args, **kwargs):
        # Configuration for Confluent Kafka Consumer
        conf = {
            'bootstrap.servers': '3.110.42.80:9092',  # Kafka broker address
            'group.id': 'vendor-location-group',  # Required group ID for the consumer
            'client.id': 'vendor-location-consumer',  # Client identifier for the consumer
            'auto.offset.reset': 'earliest',  # Start reading at the earliest available message
        }

        # Create a Kafka consumer instance
        consumer = Consumer(conf)
        consumer.subscribe(['vendor-location-topic'])

        self.stdout.write('Starting Kafka consumer...')
        try:
            while True:
                msg = consumer.poll(1.0)  # Poll messages from Kafka with a 1-second timeout
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue  # End of partition event, skip
                    else:
                        self.stdout.write(f"Consumer error: {msg.error()}")
                        continue
                
                # Log the raw message value
                raw_msg = msg.value().decode('utf-8')
                self.stdout.write(f"Raw Kafka message: {raw_msg}")

                # Try to parse the message as JSON
                try:
                    json_msg = json.loads(raw_msg)
                    self.handle_message(json_msg)  # Handle the message
                except json.JSONDecodeError as e:
                    self.stdout.write(f"Failed to decode message as JSON: {e}")
                    continue
        except KeyboardInterrupt:
            self.stdout.write('Kafka consumer stopped.')
        finally:
            consumer.close()  # Close the consumer on exit

    def handle_message(self, message):
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

        # Handle action based on the message
        if action == 'create':
            self.create_location(data, vendor, customer)
        elif action == 'update':
            self.update_location(data, vendor, customer)

    def create_location(self, data, vendor, customer):
        serializer = VendorLocationSerializer(data=data)
        if serializer.is_valid():
            # Deactivate previous active locations if necessary
            if data.get('is_active'):
                VendorLocation.objects.filter(vendor=vendor, is_active=True).update(is_active=False)
            location = serializer.save(vendor=vendor)
            self.stdout.write(f"Location created for vendor {vendor.id}")
            self.stdout.write(json.dumps(VendorLocationSerializer(location).data, indent=4))
            self.send_location_to_customer(customer.id, location)
        else:
            self.stdout.write(str(serializer.errors))

    def update_location(self, data, vendor, customer):
        try:
            # Find the active location for the vendor
            location = VendorLocation.objects.get(vendor=vendor, is_active=True)
        except VendorLocation.DoesNotExist:
            self.stdout.write(f"Active location not found for vendor {vendor.id}")
            return

        serializer = VendorLocationSerializer(location, data=data, partial=True)
        if serializer.is_valid():
            # Deactivate previous active locations if necessary
            if data.get('is_active'):
                VendorLocation.objects.filter(vendor=vendor, is_active=True).update(is_active=False)
            updated_location = serializer.save(vendor=vendor)
            self.stdout.write(f"Location updated for vendor {vendor.id}")
            self.stdout.write(json.dumps(VendorLocationSerializer(updated_location).data, indent=4))
            self.send_location_to_customer(customer.id, updated_location)
        else:
            self.stdout.write(str(serializer.errors))

    def send_location_to_customer(self, customer_id, location):
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
