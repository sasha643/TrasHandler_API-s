from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomerAuth, VendorAuth

class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        print(request.data)
        if not auth_header:
            raise AuthenticationFailed('Authorization header is missing or invalid.')

        auth_token = auth_header.split()[1]  # Assuming token is passed as "Bearer <token>"

        try:
            vendor_auth = VendorAuth.objects.get(token=auth_token)
            return self.authenticate_vendor(vendor_auth, request)
        except VendorAuth.DoesNotExist:
            try:
                customer_auth = CustomerAuth.objects.get(token=auth_token)
                return self.authenticate_customer(customer_auth, request)
            except CustomerAuth.DoesNotExist:
                raise AuthenticationFailed('Invalid token or user not found.')

    def authenticate_vendor(self, vendor_auth, request):
        if request.method == 'GET':
            vendor_id = request.parser_context['kwargs'].get('vendor_id')
        else:
            vendor_id = request.data.get('vendor_id')

        if not vendor_id:
            raise AuthenticationFailed('Vendor ID is required for authentication.')

        if int(vendor_auth.id) == int(vendor_id):
            return (vendor_auth, vendor_auth)  # Returning vendor_auth object as both user and auth
        else:
            raise AuthenticationFailed('You are not authenticated as a vendor.')

    def authenticate_customer(self, customer_auth, request):
        if request.method == 'GET':
            customer_id = request.parser_context['kwargs'].get('customer_id')
        else:
            customer_id = request.data.get('customer_id')

        if not customer_id:
            raise AuthenticationFailed('Customer ID is required for authentication.')

        if int(customer_auth.id) == int(customer_id):
            return (customer_auth, customer_auth)  # Returning customer_auth object as both user and auth
        else:
            raise AuthenticationFailed('You are not authenticated as a customer.')