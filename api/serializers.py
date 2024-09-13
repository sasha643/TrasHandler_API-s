import email

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
        fields = ('name', 'email', 'mobile_no')
        

    def create(self, validated_data):
        customer_auth = CustomerAuth.objects.create_user(**validated_data)
        return customer_auth

class PhoneNumberSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)


class VendorAuthRegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorAuth
        fields = ('name', 'email', 'mobile_no')

    def create(self, validated_data):
        vendor_auth = VendorAuth.objects.create(**validated_data)
        return vendor_auth
   
class CustomerAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAuth
        fields = ('name', 'email', 'mobile_no')


class VendorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAuth
        fields = ['name', 'mobile_no', 'email']


class CustomerSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)

class VendorSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)

class PhotoUploadSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PhotoUpload
        fields = '__all__'



class VendorCompleteProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = VendorCompleteProfile
        fields = ['gstin_number', 'business_name', 'pan_card', 'business_photos']

    def create(self, validated_data):
        
        profile = VendorCompleteProfile.objects.create(**validated_data)
        return profile

    
from django.contrib.gis.geos import Point

class CustomerLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    location = serializers.SerializerMethodField(read_only=True)  # To return the location as latitude/longitude
    
    class Meta:
        model = CustomerLocation
        fields = ['latitude', 'longitude', 'location']

    def get_location(self, obj):
        # This returns location as {'latitude': ..., 'longitude': ...}
        if obj.location:
            return {'latitude': obj.location.y, 'longitude': obj.location.x}
        return None

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        point = Point(longitude, latitude)
        validated_data['location'] = point
        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude)
        return super().update(instance, validated_data)
    
class VendorLocationSerializer(serializers.ModelSerializer):
    latitude = serializers.FloatField(write_only=True)
    longitude = serializers.FloatField(write_only=True)
    location = serializers.SerializerMethodField(read_only=True)  # To return the location as latitude/longitude
    
    class Meta:
        model = VendorLocation
        fields = ['latitude', 'longitude', 'location']

    def get_location(self, obj):
        # This returns location as {'latitude': ..., 'longitude': ...}
        if obj.location:
            return {'latitude': obj.location.y, 'longitude': obj.location.x}
        return None

    def create(self, validated_data):
        latitude = validated_data.pop('latitude')
        longitude = validated_data.pop('longitude')
        point = Point(longitude, latitude)
        validated_data['location'] = point
        return super().create(validated_data)

    def update(self, instance, validated_data):
        latitude = validated_data.pop('latitude', None)
        longitude = validated_data.pop('longitude', None)
        if latitude is not None and longitude is not None:
            instance.location = Point(longitude, latitude)
        return super().update(instance, validated_data)

class VendorLocationStatusUpdateSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField()

    class Meta:
        model = VendorLocation
        fields = ['is_active']

class PickupRequestSerializer(serializers.ModelSerializer):
    customer_name = serializers.ReadOnlyField(source='customer.user.name')
    customer_email = serializers.ReadOnlyField(source='customer.user.email')
    customer_mobile_no = serializers.ReadOnlyField(source='customer.user.mobile_no')
    vendor_id = serializers.ReadOnlyField(source='vendor.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = PickupRequest
        fields = [ 'latitude', 'longitude', 'vendor_id', 'vendor_name', 'status', 'customer_name', 'customer_email', 'customer_mobile_no']

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
        fields = ['id', 'name', 'email', 'mobile_no']        

class UpdatePickupRequestStatusSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PickupRequest.STATUS_CHOICES)

class RejectAndReassignPickupRequestSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()

class RejectPickupRequestSerializer(serializers.Serializer):
    pickup_request_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False)