from django.urls import re_path
from .consumers import PickupRequestConsumer

websocket_urlpatterns = [
    re_path(r'ws/customer/(?P<customer_id>\d+)/pickup-request/$', PickupRequestConsumer.as_asgi()),
]
