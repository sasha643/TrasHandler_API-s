import email
from typing import Required
from attr import fields
from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer as BaseTokenObtainPairSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from .models import CustomUser


User = get_user_model()



class CustomerAuthRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomerAuth
        fields = ('name', 'email', 'phone_number')
        

    def create(self, validated_data):
        customer_auth = CustomerAuth.objects.create_user(**validated_data)
        return customer_auth

class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


class VendorAuthRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorAuth
        fields = ('name', 'email', 'phone_number')

    def create(self, validated_data):
        vendor_auth = VendorAuth.objects.create(**validated_data)
        return vendor_auth
   
class CustomerAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAuth
        fields = ('name', 'email', 'phone_number')


class VendorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAuth
        fields = ('name', 'email', 'phone_number')
        

class CustomerSigninSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VendorSigninSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class PhotoUploadSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PhotoUpload
        fields = '__all__'


class CustomerLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

    class Meta:
        model = CustomerLocation
        fields = ['latitude', 'longitude']

    def create(self, validated_data):
        # Customer will be assigned in the viewset's perform_create method
        location = CustomerLocation.objects.create(**validated_data)
        return location

    def update(self, instance, validated_data):
        # Customer will be handled in the viewset's perform_update method
        instance.latitude = validated_data.get('latitude', instance.latitude)
        instance.longitude = validated_data.get('longitude', instance.longitude)
        instance.save()
        return instance



class VendorCompleteProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCompleteProfile
        fields = ['gstin_number', 'business_name', 'pan_card', 'business_photos']

    def create(self, validated_data):
        
        profile = VendorCompleteProfile.objects.create(**validated_data)
        return profile
    
class VendorLocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorLocation
        fields = ['latitude', 'longitude']

    def create(self, validated_data):
        location = VendorLocation.objects.create(**validated_data)
        return location

class VendorLocationStatusUpdateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()

    class Meta:
        model = VendorLocation
        fields = ['is_active']

class PickupRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.user.name')
    customer_email = serializers.ReadOnlyField(source='customer.user.email')
    customer_phone_number = serializers.ReadOnlyField(source='customer.user.phone_number')
    vendor_id = serializers.ReadOnlyField(source='vendor.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = PickupRequest
        fields = [ 'latitude', 'longitude', 'vendor_id', 'vendor_name', 'status', 'customer_name', 'customer_email', 'customer_phone_number']

    def create(self, validated_data):
        user = self.context['request'].user
        customer = CustomerAuth.objects.get(id=user.id)
        request = PickupRequest.objects.create(customer=customer, **validated_data)
        return request

class VendorDetailsSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='user.id')
    name = serializers.CharField(source='user.name')
    email = serializers.EmailField(source='user.email')

    class Meta:
        model = VendorAuth
        fields = ['id', 'name', 'email', 'phone_number']        

class UpdatePickupRequestStatusSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PickupRequest.STATUS_CHOICES)

class RejectAndReassignPickupRequestSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()

class RejectPickupRequestSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False)