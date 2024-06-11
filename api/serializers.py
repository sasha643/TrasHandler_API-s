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
        

class VendorSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)


class PhotoUploadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PhotoUpload
        fields = '__all__'

class CustomerSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)


class CustomerLocationSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CustomerLocation
        fields = ['customer_id', 'latitude', 'longitude']

    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        customer = CustomerAuth.objects.get(id=customer_id)
        location = CustomerLocation.objects.create(customer=customer, **validated_data)
        return location

class VendorCompleteProfileSerializer(serializers.ModelSerializer):
    vendor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VendorCompleteProfile
        fields = ['vendor_id', 'gstin_number', 'business_name', 'pan_card', 'business_photos']

    def create(self, validated_data):
        vendor_id = validated_data.pop('vendor_id')
        vendor = VendorAuth.objects.get(id=vendor_id)
        profile = VendorCompleteProfile.objects.create(vendor=vendor, **validated_data)
        return profile
