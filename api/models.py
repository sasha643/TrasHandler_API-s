from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin




class AppUserManager(BaseUserManager):
	def create_user(self, email, **extra_fields):
		if not email:
			raise ValueError('An email is required.')
		
		email = self.normalize_email(email)
		user = self.model(email=email, **extra_fields)
		user.save(using=self._db)
		return user
	def create_superuser(self, email, **extra_fields):
         extra_fields.setdefault('is_staff', True)
         extra_fields.setdefault('is_superuser', True)

         if extra_fields.get('is_staff') is not True:
              raise ValueError('SuperUser must have is_staff=True.')
         if extra_fields.get('is_superuser') is not True:
              raise ValueError('Superuser must have is_superuser=True.')

         return self.create_user(email, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
	user_id = models.AutoField(primary_key=True)
	email = models.EmailField(max_length=50, unique=True)
	name = models.CharField(max_length=50)
	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = []
	objects = AppUserManager()
	def __str__(self):
		return self.name


class CustomerAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,)
    mobile_no = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f'{self.user.name}'


class VendorAuth(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True)
    mobile_no = models.CharField(max_length=15, unique=True)

    def __str__(self):
        return f'{self.user.name}'

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
        return f'{self.user.username} - {self.landmark}'

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


    def __str__(self):
        return f'Request by {self.customer.name} - {self.status}'


