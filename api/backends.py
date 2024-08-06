# backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import CustomerAuth, VendorAuth, CustomUser

User = CustomUser

class MobileNoBackend(BaseBackend):
    def authenticate(self, request, mobile_no=None, **kwargs):
        if mobile_no is None:
            return None
        try:
            
            user = CustomUser.objects.get(mobile_no=mobile_no)
            print(f"Authenticated User: {user}")
            if hasattr(user, 'customerauth'):
                return user.customerauth
            elif hasattr(user, 'vendorauth'):
                return user.vendorauth
            else:
                return None
        except (CustomUser.DoesNotExist, CustomerAuth.DoesNotExist, VendorAuth.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        