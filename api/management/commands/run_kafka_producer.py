from django.core.management.base import BaseCommand
import json
from api.producers import send_location_update

class Command(BaseCommand):
    help = 'Send Kafka messages for vendor location updates'

    def add_arguments(self, parser):
        parser.add_argument('--action', type=str, required=True)
        parser.add_argument('--vendor_id', type=int, required=True)
        parser.add_argument('--data', type=str, required=True)

    def handle(self, *args, **options):
        action = options['action']
        vendor_id = options['vendor_id']
        data = options['data']

        # Parse data from JSON string
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            self.stdout.write(self.style.ERROR('Invalid JSON data'))
            return

        send_location_update(action, data, vendor_id)
        self.stdout.write(self.style.SUCCESS('Message sent successfully'))
