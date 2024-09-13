from django.contrib import admin
from .models import *
from django.contrib.gis.admin import OSMGeoAdmin
# Register your models here.

class NotificationModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'message','created_at', 'sent', 'recipient_type']
    # search_fields = ['recipient_type']

class CustomerAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','email', 'mobile_no']


class VendorAuthModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'mobile_no']


class PhotoUploadModelAdmin(admin.ModelAdmin):
    list_display = ['id','customer', 'photo', 'description', 'landmark', 'time_slot']



class VendorCompleteProfileModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'vendor', 'gstin_number', 'business_name', 'pan_card', 'business_photos']
    search_fields = ['vendor__name', 'vendor__mobile_no']



@admin.register(VendorLocation)
class VendorLocationModelAdmin(OSMGeoAdmin):
    default_lon = 0  # Default longitude (example: for centering the map)
    default_lat = 0  # Default latitude (example: for centering the map)
    default_zoom = 12  # Default zoom level of the map
    list_display = ['id', 'vendor', 'location', 'is_active']

@admin.register(CustomerLocation)
class CustomerLocationModelAdmin(OSMGeoAdmin):
    default_lon = 0  # Default longitude (example: for centering the map)
    default_lat = 0  # Default latitude (example: for centering the map)
    default_zoom = 12  # Default zoom level of the map
    list_display = ['id', 'customer', 'location', 'is_active']


class PickupRequestModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'vendor', 'status', 'created_at','accepted_time', 'get_rejected_vendors', 'remarks']
    search_fields = ['customer__name', 'customer__mobile_no', 'vendor__name', 'vendor__mobile_no', 'status']

    def get_rejected_vendors(self, obj):
        return obj.get_rejected_vendors()
    get_rejected_vendors.short_description = 'Rejected Vendors'

class UserTokenModelAdmin(admin.ModelAdmin):
    list_display = ('user', 'access_token', 'refresh_token','token_created_at')
    
admin.site.register(CustomerAuth, CustomerAuthModelAdmin)
admin.site.register(VendorAuth, VendorAuthModelAdmin)
admin.site.register(PhotoUpload, PhotoUploadModelAdmin)
admin.site.register(VendorCompleteProfile, VendorCompleteProfileModelAdmin)
admin.site.register(PickupRequest, PickupRequestModelAdmin)
admin.site.register(CustomUser)
admin.site.register(Notification, NotificationModelAdmin)
admin.site.register(UserToken, UserTokenModelAdmin)
