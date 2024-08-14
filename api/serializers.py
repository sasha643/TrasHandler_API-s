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

    def validate(self, data):
        email = data.get('email', None)
        mobile_no = data.get('mobile_no')

        if email is None or email == '':
            email = "Not Provided"
        data['email'] = email

        if self.instance:
            # When updating, exclude the current instance from uniqueness checks
            if (email != 'Not Provided' and CustomerAuth.objects.filter(email=email).exclude(pk=self.instance.pk).exists()) or CustomerAuth.objects.filter(mobile_no=mobile_no).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Account with these credentials already exists, try logging in")
        else:
            # When creating, ensure no existing records have the same email or mobile number
            if (email != 'Not Provided' and CustomerAuth.objects.filter(email=email).exists()) or CustomerAuth.objects.filter(mobile_no=mobile_no).exists():
                raise serializers.ValidationError("Account with these credentials already exists, try logging in")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        email = validated_data.get('email', instance.email)
        mobile_no = validated_data.get('mobile_no', instance.mobile_no)

        if email is None or email == '':
            email = "Not Provided"
        validated_data['email'] = email

        if (email != 'Not Provided' and CustomerAuth.objects.filter(email=email).exclude(pk=instance.pk).exists()) or CustomerAuth.objects.filter(mobile_no=mobile_no).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Account with these credentials already exists, try logging in")

        return super().update(instance, validated_data)

class VendorAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAuth
        fields = ['name', 'mobile_no', 'email']

    def validate(self, data):
        email = data.get('email', None)
        mobile_no = data.get('mobile_no')

        if email is None or email == '':
            email = "Not Provided"
        data['email'] = email

        if self.instance:
            # When updating, exclude the current instance from uniqueness checks
            if (email != 'Not Provided' and VendorAuth.objects.filter(email=email).exclude(pk=self.instance.pk).exists()) or VendorAuth.objects.filter(mobile_no=mobile_no).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Account with these credentials already exists, try logging in")
        else:
            # When creating, ensure no existing records have the same email or mobile number
            if (email != 'Not Provided' and VendorAuth.objects.filter(email=email).exists()) or VendorAuth.objects.filter(mobile_no=mobile_no).exists():
                raise serializers.ValidationError("Account with these credentials already exists, try logging in")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        email = validated_data.get('email', instance.email)
        mobile_no = validated_data.get('mobile_no', instance.mobile_no)

        if email is None or email == '':
            email = "Not Provided"
        validated_data['email'] = email

        if (email != 'Not Provided' and VendorAuth.objects.filter(email=email).exclude(pk=instance.pk).exists()) or VendorAuth.objects.filter(mobile_no=mobile_no).exclude(pk=instance.pk).exists():
            raise serializers.ValidationError("Account with these credentials already exists, try logging in")

        return super().update(instance, validated_data)
      

class CustomerSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)

class VendorSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)

class PhotoUploadSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    
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