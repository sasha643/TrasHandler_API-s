from rest_framework import serializers
from .models import *


class CustomerAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerAuth
        fields = ['id', 'name', 'mobile_no', 'email']

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
        fields = ['id', 'name', 'mobile_no', 'email']

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
      

class VendorSigninSerializer(serializers.Serializer):
    mobile_no = serializers.CharField(max_length=15)


class PhotoUploadSerializer(serializers.ModelSerializer):
    customer_id = serializers.IntegerField(write_only=True)
    
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

class RejectAndReassignPickupRequestSerializer(serializers.Serializer):
    vendor_id = serializers.IntegerField()
    pickup_request_id = serializers.IntegerField()

class RejectPickupRequestSerializer(serializers.Serializer):
    customer_id = serializers.IntegerField()
    pickup_request_id = serializers.IntegerField()
    remarks = serializers.CharField(required=False)