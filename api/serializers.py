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
    customer_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = PhotoUpload
        fields = ['customer_id', 'photo', 'description', 'landmark', 'time_slot']

        def create(self, validated_data):
            customer_id = validated_data.pop('customer_id')
            customer = CustomerAuth.objects.get(id=customer_id)
            profile = PhotoUpload.objects.create(customer=customer, **validated_data)
            return profile

class CustomerSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)

class AddressSerializer(serializers.Serializer):
    street = serializers.CharField(max_length=100)
    city = serializers.CharField(max_length=50)
    state = serializers.CharField(max_length=50)
    zip_code = serializers.CharField(max_length=10)
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()

class CustomerLocationSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    address = AddressSerializer(many=True)

    class Meta:
        model = CustomerLocation
        fields = ['customer_id', 'address']

    def create(self, validated_data):
        customer_id = validated_data.pop('customer_id')
        customer = CustomerAuth.objects.get(id=customer_id)
        location = CustomerLocation.objects.create(customer=customer, **validated_data)
        return location

    def update(self, instance, validated_data):
        instance.address = validated_data.get('address', instance.address)
        instance.save()
        return instance
    
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
        fields = ['customer_id', 'latitude', 'longitude', 'vendor_id', 'vendor_name', 'status', 'customer_name', 'customer_email', 'customer_mobile_no', 'landmark', 'timeslots', 'description','photo']

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

class RejectAndReassignPickupRequestSerializer(serializers.Serializer):
    vendor_id = serializers.IntegerField()
    pickup_request_id = serializers.IntegerField()

class RejectPickupRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    pickup_request_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False)
