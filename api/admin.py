from django.contrib import admin
from .models import *

# Register your models here.

class CustomerAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class VendorAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class PhotoUploadModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'photo', 'description', 'landmark', 'time_slot']

class CustomerLocationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'latitude', 'longitude']
    search_fields = ['customer__name', 'customer__mobile_no']

class VendorCompleteProfileModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'gstin_number', 'business_name', 'pan_card', 'business_photos']
    search_fields = ['vendor__name', 'vendor__mobile_no']

admin.site.register(CustomerAuth, CustomerAuthModelAdmin)
admin.site.register(VendorAuth, VendorAuthModelAdmin)
admin.site.register(PhotoUpload, PhotoUploadModelAdmin)
admin.site.register(CustomerLocation, CustomerLocationModelAdmin)
admin.site.register(VendorCompleteProfile, VendorCompleteProfileModelAdmin)
