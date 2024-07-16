from rest_framework.permissions import BasePermission
from .models import CustomerAuth, VendorAuth

class IsCustomerAndAuthenticated(BasePermission):
    def has_permission(self, request, view):
        is_authenticated = bool(request.user and request.user.is_authenticated)
        print(f'Is auth: {is_authenticated}')
        return is_authenticated

class IsVendorAndAuthenticate(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and hasattr(request.user, 'vendorauth'))
