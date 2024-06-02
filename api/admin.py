from django.contrib import admin
from .models import *

# Register your models here.

class CustomerAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class VendorAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class PhotoUploadModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'photo', 'description', 'landmark', 'time_slot']

class VendorLocationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'latitude', 'longitude']

admin.site.register(CustomerAuth, CustomerAuthModelAdmin)
admin.site.register(VendorAuth, VendorAuthModelAdmin)
admin.site.register(PhotoUpload, PhotoUploadModelAdmin)
admin.site.register(VendorLocation, VendorLocationModelAdmin)