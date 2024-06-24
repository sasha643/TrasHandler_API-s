from django.contrib.auth.backends import BaseBackend
from .models import CustomerAuth, VendorAuth, User

class CustomerBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            customer = CustomerAuth.objects.get(user=user)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, CustomerAuth.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

class VendorBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        try:
            user = User.objects.get(email=email)
            vendor = VendorAuth.objects.get(user=user)
            if user.check_password(password):
                return user
        except (User.DoesNotExist, VendorAuth.DoesNotExist):
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
