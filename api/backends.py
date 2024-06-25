# backends.py
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import CustomerAuth, VendorAuth

User = get_user_model()

class MobileNoBackend(BaseBackend):
    def authenticate(self, request, mobile_no=None, is_customer=False, **kwargs):
        try:
            if is_customer:
                user = User.objects.get(customerauth__mobile_no=mobile_no)
            else:
                user = User.objects.get(vendorauth__mobile_no=mobile_no)
            return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            return None  # or handle the conflict

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None