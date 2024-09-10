import os
from django.urls import path, include
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.schemas import get_schema_view
from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path, re_path
from django.views.static import serve


from .views import *

customer_auth_router = routers.SimpleRouter()
customer_auth_router.register(r'customerauth', CustomerAuthViewSet)

vendor_auth_router = routers.SimpleRouter()
vendor_auth_router.register(r'vendorauth', VendorAuthViewSet)


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

doc_path = os.path.join(os.path.dirname(__file__), 'docs/_build/html')



#update_status_router = routers.SimpleRouter()
#update_status_router.register(r'pickup-request-status', PickupRequestStatusUpdateViewSet, basename='pickup-request-status')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(), name="schema"),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name="schema")),
    re_path(r'^documentation/$', serve, {'path': 'index.html', 'document_root': doc_path}),
    
    # Serve other Sphinx documentation files
    re_path(r'^documentation/(?P<path>.*)$', serve, {'document_root': doc_path}),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/customer/register/', CustomerAuthRegisterView.as_view(), name='customer-register'),
    path('api/auth/vendor/register/', VendorAuthRegisterView.as_view(), name='vendor-register'),
    path('customersignin/', CustomerSigninView.as_view(), name='customer-login'),
    path('vendorsignin/', VendorSigninView.as_view(), name='vendor-login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(customer_auth_router.urls)),
    path('', include(vendor_auth_router.urls)),
    path('', include(upload_auth_router.urls)),
    path('', include(vendor_location_router.urls)),
    path('', include(customer_location_router.urls)),
    path('', include(vendor_complete_profile_router.urls)),
    path('', include(vendor_status_router.urls)),
    #path('', include(nearest_vendor_router.urls)),
    path('vendor/profile/<int:vendor_id>/', VendorProfileDetailView.as_view(), name='vendor-profile-detail'),
    path('vendor/pickup-requests/<int:vendor_id>/', VendorPickupRequestView.as_view(), name='vendor-pickup-requests'),
    path('customer/<int:customer_id>/pickup-request/', CustomerPickupRequestView.as_view(), name='customer-pickup-request'),
    
]



if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
