from rest_framework import serializers
from .models import *
from django.contrib.auth import get_user_model


User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class CustomerAuthRegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = CustomerAuth
        fields = ('user', 'mobile_no')

    # def

    # def create(self, validated_data):
    #     customer = CustomerAuth.objects.create(
    #         mobile_no=validated_data['mobile_no'],
    #         name=validated_data['name'],
    #     )
    #     # customer.set_password(validated_data['password'])
    #     customer.save()
    #     return customer

 

class VendorAuthRegisterSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta:
        model = VendorAuth
        fields = ('user', 'mobile_no')

        # def create(self, validated_data):
        #     vendor = VendorAuth.objects.create(
        #         mobile_no=validated_data['mobile_no'],
        #         name=validated_data['name'],
        #     )
        #     # vendor.set_password(validated_data['password'])
        #     vendor.save()
        #     return vendor
   
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
    
class VendorLocationSerializer(serializers.ModelSerializer):
    vendor_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = VendorLocation
        fields = ['vendor_id', 'latitude', 'longitude']

    def create(self, validated_data):
        vendor_id = validated_data.pop('vendor_id')
        vendor = VendorAuth.objects.get(id=vendor_id)
        location = VendorLocation.objects.create(vendor=vendor, **validated_data)
        return location

class VendorLocationStatusUpdateSerializer(serializers.ModelSerializer):
    vendor_id = serializers.IntegerField(write_only=True)
    is_active = serializers.BooleanField()

    class Meta:
        model = VendorLocation
        fields = ['vendor_id', 'is_active']

class PickupRequestSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    customer_name = serializers.ReadOnlyField(source='customer.name')
    customer_email = serializers.ReadOnlyField(source='customer.email')
    customer_mobile_no = serializers.ReadOnlyField(source='customer.mobile_no')
    vendor_id = serializers.ReadOnlyField(source='vendor.id')
    vendor_name = serializers.ReadOnlyField(source='vendor.name')

    class Meta:
        model = PickupRequest
        fields = ['customer_id', 'latitude', 'longitude', 'vendor_id', 'vendor_name', 'status', 'customer_name', 'customer_email', 'customer_mobile_no']

    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        customer = CustomerAuth.objects.get(id=customer_id)
        request = PickupRequest.objects.create(customer=customer, **validated_data)
        return request

class VendorDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = VendorAuth
        fields = ['id', 'name', 'email', 'mobile_no']        

class UpdatePickupRequestStatusSerializer(serializers.Serializer):
    vendor_id = serializers.IntegerField()
    pickup_request_id = serializers.IntegerField()
    status = serializers.ChoiceField(choices=PickupRequest.STATUS_CHOICES)

