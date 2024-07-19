# tasks.py
from celery import shared_task
from .models import *
from .serializers import *
from .functions import *  # Assuming haversine function is in functions.py
import logging

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def process_pickup_request(self, customer_id, latitude, longitude):
    try:
        # Fetch customer
        customer = CustomerAuth.objects.get(id=customer_id)

        # Find nearest active vendor
        active_vendors = VendorLocation.objects.filter(is_active=True)
        min_distance = float('inf')
        nearest_vendor = None

        for vendor in active_vendors:
            distance = haversine(float(latitude), float(longitude), vendor.latitude, vendor.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest_vendor = vendor

        if nearest_vendor:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                vendor=nearest_vendor.vendor,
                status='Request Sent'
            )
        else:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                status='No Active Vendors Available'
            )
        return PickupRequestSerializer(pickup_request).data

    except CustomerAuth.DoesNotExist:
        logger.error(f'Customer profile not found for ID {customer_id}')
        raise self.retry(exc=ValueError('Customer profile not found'), countdown=60, max_retries=3)

    except Exception as exc:
        logger.error(f'Error processing pickup request: {exc}')
        raise self.retry(exc=exc, countdown=60, max_retries=3)
