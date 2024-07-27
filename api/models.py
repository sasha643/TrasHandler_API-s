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

    customer = models.ForeignKey(CustomerAuth, on_delete=models.CASCADE)
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


