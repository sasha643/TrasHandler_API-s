from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()


class CustomerAuth(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.name}'

class VendorAuth(models.Model):
    user = models.OneToOneField(User, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True, blank=True)
    mobile_no = models.CharField(max_length=15)

    def __str__(self):
        return f'{self.name}'

class PhotoUpload(models.Model):
    TIME_SLOTS = [
        ('morning', 'Morning'),
        ('afternoon', 'Afternoon'),
        ('evening', 'Evening'),
        ('night', 'Night'),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='photos/')
    description = models.TextField()
    landmark = models.CharField(max_length=255)
    time_slot = models.CharField(max_length=10, choices=TIME_SLOTS)

    def __str__(self):
        return f'{self.user.username} - {self.landmark}'


class VendorLocation(models.Model):
    vendor = models.OneToOneField(VendorAuth, on_delete=models.CASCADE, related_name='location')
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)