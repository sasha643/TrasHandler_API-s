from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.schemas import get_schema_view
from .views import *

customer_auth_router = routers.SimpleRouter()
customer_auth_router.register(r'customerauth', CustomerAuthViewSet)

customer_signin_router = routers.SimpleRouter()
customer_signin_router.register(r'customersignin', CustomerSigninViewSet, basename='customersignin')

vendor_auth_router = routers.SimpleRouter()
vendor_auth_router.register(r'vendorauth', VendorAuthViewSet)

vendor_signin_router = routers.SimpleRouter()
vendor_signin_router.register(r'vendorsignin', VendorSigninViewSet, basename='vendorsignin')

upload_auth_router = routers.SimpleRouter()
upload_auth_router.register(r'upload', PhotoUploadViewSet)

vendor_location_router = routers.SimpleRouter()
vendor_location_router.register(r'vend_location', VendorLocationViewSet, basename='vend_location')

vendor_status_router = routers.SimpleRouter()
vendor_status_router.register(r'vendor_status', VendorStatusUpdateViewSet, basename='vendor_status')

customer_location_router = routers.SimpleRouter()
customer_location_router.register(r'cust_location', CustomerLocationViewSet, basename='cust_location')

vendor_complete_profile_router = routers.SimpleRouter()
vendor_complete_profile_router.register(r'vendor-complete-profile', VendorCompleteProfileViewSet, basename='vendor-complete-profile')

vendor_notification_router = routers.SimpleRouter()
vendor_notification_router.register(r'pickup-request', PickupRequestViewSet, basename='pickup-request')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
    path('', include(customer_auth_router.urls)),
    path('', include(vendor_auth_router.urls)),
    path('', include(upload_auth_router.urls)),
    path('', include(vendor_location_router.urls)),
    path('', include(customer_location_router.urls)),
    path('', include(vendor_signin_router.urls)),
    path('', include(customer_signin_router.urls)),
    path('', include(vendor_complete_profile_router.urls)),
    path('', include(vendor_status_router.urls)),
    path('vendor/profile/<int:vendor_id>/', VendorProfileDetailView.as_view(), name='vendor-profile-detail'),
    path('vendor/pickup-requests/<int:vendor_id>/', VendorPickupRequestView.as_view(), name='vendor-pickup-requests'),
    path('', include(vendor_notification_router.urls)),
    path('vendor/pickup-requests/<int:vendor_id>/', VendorPickupRequestView.as_view(), name='vendor-pickup-requests'),
    path('update-pickup-request-status/', UpdatePickupRequestStatusView.as_view(), name='update-pickup-request-status'),
    path('customer/<int:customer_id>/pickup-request/', CustomerPickupRequestView.as_view(), name='customer-pickup-request'),
    path('reject-and-reassign-pickup-request/', RejectAndReassignPickupRequestView.as_view(), name='reject-and-reassign-pickup-request'),
    path('customer/reject-pickup-request/', CustomerRejectPickupRequestView.as_view(), name='customer-reject-pickup-request'),
    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
