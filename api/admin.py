from django.contrib import admin
from .models import *

# Register your models here.

class CustomerAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class VendorAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']

class PhotoUploadModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'photo', 'description', 'landmark', 'time_slot']

class CustomerLocationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'latitude', 'longitude']
    search_fields = ['customer__name', 'customer__mobile_no']

class VendorCompleteProfileModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'gstin_number', 'business_name', 'pan_card', 'business_photos']
    search_fields = ['vendor__name', 'vendor__mobile_no']

class VendorLocationModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'latitude', 'longitude', 'is_active']
    search_fields = ['vendor__name', 'vendor__mobile_no']

class PickupRequestModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'status', 'get_rejected_vendors', 'remarks']
    search_fields = ['customer__name', 'customer__mobile_no', 'vendor__name', 'vendor__mobile_no', 'status']

    def get_rejected_vendors(self, obj):
        return obj.get_rejected_vendors()
    get_rejected_vendors.short_description = 'Rejected Vendors'

admin.site.register(CustomerAuth, CustomerAuthModelAdmin)
admin.site.register(VendorAuth, VendorAuthModelAdmin)
admin.site.register(PhotoUpload, PhotoUploadModelAdmin)
admin.site.register(CustomerLocation, CustomerLocationModelAdmin)
admin.site.register(VendorCompleteProfile, VendorCompleteProfileModelAdmin)
admin.site.register(VendorLocation, VendorLocationModelAdmin)
admin.site.register(PickupRequest, PickupRequestModelAdmin)
