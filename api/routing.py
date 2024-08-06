from django.urls import path, include, re_path
from .consumers import *

websocket_urlpatterns = [
    re_path(r'^ws/notifications/$', NotificationConsumer.as_asgi()),
    # Route for updating pickup request status
    re_path(r'^ws/update_pickup_request_status/$', UpdatePickupRequestStatusConsumer.as_asgi(), name='update_pickup_request_status'),

    # Route for rejecting and reassigning pickup requests
    re_path(r'^ws/reject_and_reassign_pickup_request/$', RejectAndReassignPickupRequestConsumer.as_asgi(), name='reject_and_reassign_pickup_request'),
    re_path(r'^ws/customer_reject_pickup_request/$', CustomerRejectPickupRequestConsumer.as_asgi(), name='customer_reject_pickup_request'),
    re_path(r'^ws/pickup_request/$', PickupRequestConsumer.as_asgi(), name='pickup_request')
    
]
