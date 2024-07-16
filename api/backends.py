# backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import CustomerAuth, VendorAuth, CustomUser

User = CustomUser

class MobileNoBackend(BaseBackend):
    def authenticate(self, request, phone_number=None, **kwargs):
        if phone_number is None:
            return None
        try:
            
            user = CustomUser.objects.get(phone_number=phone_number)
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
        
from sms.backends.base import BaseSmsBackend        
class YourSmsBackend(BaseSmsBackend):
    def send_messages(self, messages):
        for message in messages:
            # Implement SMS sending logic here
            print(f"Sending SMS to {message.to} with content {message.body}")
        return len(messages)