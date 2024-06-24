from rest_framework.permissions import BasePermission
from .models import CustomerAuth, VendorAuth

class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'customerauth') and isinstance(request.user.customerauth, CustomerAuth)

class IsVendor(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'vendorauth') and isinstance(request.user.vendorauth, VendorAuth)
