from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from phonenumber_field.modelfields import PhoneNumberField
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin




class CustomUserManager(BaseUserManager):
    def create_user(self, email, phone_number, password=None, **extra_fields):
        if not email:
            raise ValueError('An email is required.')
        if not phone_number:
            raise ValueError('The mobile number must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_unusable_password()
        user.save(using=self._db)
        return user
    def create_superuser(self, email, password, **extra_fields):
         extra_fields.setdefault('is_staff', True)
         extra_fields.setdefault('is_superuser', True)

         if not email:
            raise ValueError('The Email must be set for superuser')
         if not password:
            raise ValueError('The Password must be set for superuser')

         email = self.normalize_email(email)
         user = self.model(email=email, **extra_fields)
         user.set_password(password)

         user.save(using=self._db)
         return user


class CustomUser(AbstractBaseUser, PermissionsMixin):
        id = models.AutoField(primary_key=True)
        name = models.CharField(max_length=50)
        email = models.EmailField(max_length=100, unique=True, blank=True)
        phone_number = models.CharField(max_length=15, unique=True)
        is_active = models.BooleanField(default=True)
        is_staff = models.BooleanField(default=False)
        is_superuser = models.BooleanField(default=False)
        USERNAME_FIELD = 'email'
        REQUIRED_FIELDS = []
        objects = CustomUserManager()
        def __str__(self):
            return self.name


class CustomerAuth(CustomUser):

    def __str__(self):
        return f'{self.name}'


class VendorAuth(CustomUser):

    def __str__(self):
        return f'{self.name}'

class PhotoUpload(models.Model):
    TIME_SLOTS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')
    description = models.TextField()
    landmark = models.CharField(max_length=255)
    time_slot = models.CharField(max_length=10, choices=TIME_SLOTS)

    def __str__(self):
        return f'{self.user.name} - {self.landmark}'

class CustomerLocation(models.Model):
    customer = models.ForeignKey(CustomerAuth, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.customer.name} - {self.latitude}, {self.longitude}'
    
class VendorCompleteProfile(models.Model):
    vendor = models.ForeignKey(VendorAuth, on_delete=models.CASCADE)
    gstin_number = models.CharField(max_length=15)
    business_name = models.CharField(max_length=255)
    pan_card = models.ImageField(upload_to='pan_cards/')
    business_photos = models.ImageField(upload_to='business_photos/')

    def __str__(self):
        return f'{self.vendor.name} - {self.business_name}'
    
class VendorLocation(models.Model):
    vendor = models.ForeignKey(VendorAuth, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    is_active = models.BooleanField(default=False)
    #timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.vendor.name} - {self.latitude}, {self.longitude}'

class PickupRequest(models.Model):
    STATUS_CHOICES = [
        ('Request Sent', 'Request Sent'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    ]

    customer = models.ForeignKey(CustomerAuth, on_delete=models.CASCADE)
    latitude = models.FloatField()
    longitude = models.FloatField()
    vendor = models.ForeignKey(VendorAuth, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default="Request Sent")
    rejected_vendors = models.ManyToManyField(VendorAuth, related_name='rejected_requests', blank=True)
    remarks = models.CharField(max_length=255, blank=True, null=True) 


    def __str__(self):
        return f'Request by {self.customer.name} - {self.status}'


    def get_rejected_vendors(self):
        return ", ".join([vendor.name for vendor in self.rejected_vendors.all()])