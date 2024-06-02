from rest_framework import serializers
from .models import *


class CustomerAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAuth
        fields = '__all__'


class VendorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAuth
        fields = '__all__'


class PhotoUploadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PhotoUpload
        fields = '__all__'

class VendorLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorLocation
        read_only_fields = ['vendor'] 
        fields = ['vendor', 'latitude', 'longitude']