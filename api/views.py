from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from .models import *
from .serializers import *

# Create your views here.

User = get_user_model()

class CustomerAuthViewSet(viewsets.GenericViewSet):
    queryset = CustomerAuth.objects.all()
    serializer_class = CustomerAuthSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class VendorAuthViewSet(viewsets.GenericViewSet):
    queryset = VendorAuth.objects.all()
    serializer_class = VendorAuthSerializer
    permission_classes = [AllowAny]

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class VendorSigninViewSet(viewsets.GenericViewSet):
    serializer_class = VendorSigninSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_no = serializer.validated_data['mobile_no']

        try:
            vendor_auth = VendorAuth.objects.get(mobile_no=mobile_no)
            name = vendor_auth.name  # Get the name from the VendorAuth object
            vendor_id = vendor_auth.id  # Get the id from the VendorAuth object
            return Response({"message": "Login successful", "Welcome": name, "vendor_id": vendor_id}, status=status.HTTP_200_OK)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)
    

class PhotoUploadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Handle uploading photos
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PhotoUploadSerializer
    queryset = PhotoUpload.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    
class CustomerSigninViewSet(viewsets.GenericViewSet):
    serializer_class = CustomerSigninSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        mobile_no = serializer.validated_data['mobile_no']

        try:
            customer_auth = CustomerAuth.objects.get(mobile_no=mobile_no)
            name = customer_auth.name
            return Response({"message": "Login successful", "Welcome": name, "customer_id": customer_auth.id}, status=status.HTTP_200_OK)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
        

class CustomerLocationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = CustomerLocation.objects.all()
    serializer_class = CustomerLocationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        customer_id = request.data.get('customer_id')
        if not customer_id:
            return Response({"error": "Customer ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            customer = CustomerAuth.objects.get(id=customer_id)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)

        try:
            customer_location = CustomerLocation.objects.get(customer=customer)
            # If an entry exists, update it
            serializer = self.get_serializer(customer_location, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except CustomerLocation.DoesNotExist:
            # If no entry exists, create a new one
            data = request.data.copy()
            data['customer_id'] = customer.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        serializer.save()


class VendorCompleteProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = VendorCompleteProfile.objects.all()
    serializer_class = VendorCompleteProfileSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        vendor_id = request.data.get('vendor_id')
        if not vendor_id:
            return Response({"error": "Vendor ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = VendorAuth.objects.get(id=vendor_id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)

        try:
            vendor_complete_profile = VendorCompleteProfile.objects.get(vendor=vendor)
            # If an entry exists, update it
            serializer = self.get_serializer(vendor_complete_profile, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except VendorCompleteProfile.DoesNotExist:
            # If no entry exists, create a new one
            data = request.data.copy()
            data['vendor'] = vendor.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        serializer.save()


class VendorLocationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = VendorLocation.objects.all()
    serializer_class = VendorLocationSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        vendor_id = request.data.get('vendor_id')
        if not vendor_id:
            return Response({"error": "vendor ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = VendorAuth.objects.get(id=vendor_id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "vendor profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)

        try:
            vendor_location = VendorLocation.objects.get(vendor=vendor)
            # If an entry exists, update it
            serializer = self.get_serializer(vendor_location, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except VendorLocation.DoesNotExist:
            # If no entry exists, create a new one
            data = request.data.copy()
            data['vendor_id'] = vendor.id
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        serializer.save()

    def perform_create(self, serializer):
        serializer.save()


class VendorProfileDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, vendor_id, *args, **kwargs):
        try:
            vendor_profile = VendorCompleteProfile.objects.get(vendor_id=vendor_id)
            serializer = VendorCompleteProfileSerializer(vendor_profile)
            return Response({'business_name': serializer.data['business_name']}, status=status.HTTP_200_OK)
        except VendorCompleteProfile.DoesNotExist:
            return Response({"error": "Vendor profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)
        

class PickupRequestViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = PickupRequest.objects.all()
    serializer_class = PickupRequestSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data['customer_id']
        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']

        try:
            customer = CustomerAuth.objects.get(id=customer_id)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)

        vendors = VendorLocation.objects.all()
        min_distance = float('inf')
        nearest_vendor = None

        for vendor in vendors:
            distance = haversine(float(latitude), float(longitude), vendor.latitude, vendor.longitude)
            if distance < min_distance:
                min_distance = distance
                nearest_vendor = vendor

        if nearest_vendor:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                vendor=nearest_vendor.vendor,
                status='Request Sent'
            )
            return Response({
                "message": "Pickup request created and assigned to the nearest vendor",
                "pickup_request": PickupRequestSerializer(pickup_request).data,
            }, status=status.HTTP_201_CREATED)
        else:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                status='No Vendors Available'
            )
            return Response({"error": "No vendors found"}, status=status.HTTP_404_NOT_FOUND)
        


class VendorPickupRequestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, vendor_id, *args, **kwargs):
        try:
            vendor = VendorAuth.objects.get(id=vendor_id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found for the provided ID"}, status=status.HTTP_404_NOT_FOUND)

        pickup_requests = PickupRequest.objects.filter(vendor=vendor)
        if not pickup_requests.exists():
            return Response({"error": "No pickup requests found for the provided vendor"}, status=status.HTTP_404_NOT_FOUND)

        customer_details = [
            {
                "customer_id": request.customer.id,
                "customer_name": request.customer.name,
                "customer_mobile_no": request.customer.mobile_no,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "pickup_request_id": request.id,  # Add the pickup_request_id here
                "status": request.status,
            }
            for request in pickup_requests
        ]

        return Response(customer_details, status=status.HTTP_200_OK)

class UpdatePickupRequestStatusView(generics.GenericAPIView):
    serializer_class = UpdatePickupRequestStatusSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            vendor_id = serializer.validated_data['vendor_id']
            pickup_request_id = serializer.validated_data['pickup_request_id']
            new_status = serializer.validated_data['status']

            try:
                vendor = VendorAuth.objects.get(id=vendor_id)
            except VendorAuth.DoesNotExist:
                return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)

            try:
                pickup_request = PickupRequest.objects.get(id=pickup_request_id, vendor=vendor)
            except PickupRequest.DoesNotExist:
                return Response({"error": "Pickup request not found for the provided ID and vendor"}, status=status.HTTP_404_NOT_FOUND)

            pickup_request.status = new_status
            pickup_request.save()

            return Response({"message": "Status updated successfully", "pickup_request": PickupRequestSerializer(pickup_request).data}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class CustomerPickupRequestView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, customer_id, *args, **kwargs):
        try:
            pickup_request = PickupRequest.objects.get(customer_id=customer_id, status='Accepted')
        except PickupRequest.DoesNotExist:
            return Response({"error": "No accepted pickup requests found for the provided customer"}, status=status.HTTP_404_NOT_FOUND)

        if pickup_request.vendor is None:
            return Response({"error": "No vendor assigned to this accepted pickup request"}, status=status.HTTP_404_NOT_FOUND)

        vendor = pickup_request.vendor
        serializer = VendorDetailsSerializer(vendor)
        return Response(serializer.data, status=status.HTTP_200_OK)

class RejectAndReassignPickupRequestView(APIView):
    permission_classes = [AllowAny]
    serializer_class = RejectAndReassignPickupRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        vendor_id = serializer.validated_data['vendor_id']
        pickup_request_id = serializer.validated_data['pickup_request_id']

        try:
            vendor = VendorAuth.objects.get(id=vendor_id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            pickup_request = PickupRequest.objects.get(id=pickup_request_id, vendor=vendor)
        except PickupRequest.DoesNotExist:
            return Response({"error": "Pickup request not found for the provided ID and vendor"}, status=status.HTTP_404_NOT_FOUND)

        # Mark the current vendor as having rejected the request
        pickup_request.status = 'Rejected'
        pickup_request.rejected_vendors.add(vendor)
        pickup_request.save()

        # Find the next nearest vendor who has not rejected the request
        customer_location = (pickup_request.latitude, pickup_request.longitude)
        vendors = VendorLocation.objects.exclude(vendor__in=pickup_request.rejected_vendors.all())
        min_distance = float('inf')
        nearest_vendor = None

        for vendor_location in vendors:
            distance = haversine(
                customer_location[0], customer_location[1],
                vendor_location.latitude, vendor_location.longitude
            )
            if distance < min_distance:
                min_distance = distance
                nearest_vendor = vendor_location.vendor

        if nearest_vendor:
            pickup_request.vendor = nearest_vendor
            pickup_request.status = 'Request Sent'
            pickup_request.save()

            return Response({
                "message": "Pickup request reassigned to the next nearest vendor",
                "pickup_request": PickupRequestSerializer(pickup_request).data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No other vendors available"}, status=status.HTTP_404_NOT_FOUND)
