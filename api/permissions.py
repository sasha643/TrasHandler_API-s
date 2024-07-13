from rest_framework.permissions import BasePermission
from .models import CustomerAuth, VendorAuth
from rest_framework.exceptions import AuthenticationFailed

class IsAuthenticatedOrVendor(BasePermission):
    """
    Custom permission to allow access only to authenticated users or vendors.
    """

    def has_permission(self, request, view):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return False

        try:
            auth_token = auth_header.split()[1]  # Assuming token is passed as "Bearer <token>"
        except IndexError:
            return False

        try:
            # Check if token exists in CustomerAuth or VendorAuth
            customer_auth = CustomerAuth.objects.get(token=auth_token)
            request.user = customer_auth  # Set the authenticated user
            return True
        except CustomerAuth.DoesNotExist:
            try:
                vendor_auth = VendorAuth.objects.get(token=auth_token)
                request.user = vendor_auth  # Set the authenticated user
                return True
            except VendorAuth.DoesNotExist:
                raise AuthenticationFailed('Invalid token or user not found.')
