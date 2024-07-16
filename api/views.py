from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets, mixins, generics
from rest_framework.response import Response

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth import authenticate, get_user_model
from rest_framework_simplejwt.tokens import RefreshToken


from .models import *
from .serializers import *
from django.conf import settings
from .functions import *
from .permissions import *



# Create your views here.

User = get_user_model()


class CustomerAuthRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerAuthRegisterSerializer


class VendorAuthRegisterView(generics.CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = VendorAuthRegisterSerializer

    
class CustomerSigninView(APIView):
    permission_classes = [AllowAny]
    serializer_class = CustomerSigninSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user = authenticate(request, phone_number=phone_number)

        if user:
            try:
                customer = CustomerAuth.objects.get(id=user.id)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'name': user.name,
                    'id': user.id,
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            except CustomerAuth.DoesNotExist:
                return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid mobile number"}, status=status.HTTP_400_BAD_REQUEST)

class VendorSigninView(APIView):
    permission_classes = [AllowAny]
    serializer_class = VendorSigninSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        user = authenticate(request, phone_number=phone_number)

        if user:
            try:
                vendor = VendorAuth.objects.get(id=user.id)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login successful',
                    'name': user.name,
                    'id': user.id,
                    'access': str(refresh.access_token),
                }, status=status.HTTP_200_OK)
            except CustomerAuth.DoesNotExist:
                return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"error": "Invalid mobile number"}, status=status.HTTP_400_BAD_REQUEST)
class CustomerAuthViewSet(viewsets.GenericViewSet):
    queryset = CustomerAuth.objects.all()
    serializer_class = CustomerAuthSerializer
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    

class PhotoUploadViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Handle uploading photos
    """
    permission_classes = [IsAuthenticated]
    serializer_class = PhotoUploadSerializer
    queryset = PhotoUpload.objects.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CustomerLocationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin, mixins.UpdateModelMixin):
    queryset = CustomerLocation.objects.all()
    serializer_class = CustomerLocationSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            customer = CustomerAuth.objects.get(id=request.user.id)
        except CustomerAuth.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        location = serializer.save(customer=customer)
        response_data = self.get_serializer(location).data
        response_data['id'] = customer.id
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            customer = CustomerAuth.objects.get(id=request.user.id)
        except CustomerAuth.DoesNotExist:
            return Response({'error': 'Customer not found'}, status=status.HTTP_404_NOT_FOUND)
        
        location = serializer.save(customer=customer)
        response_data = self.get_serializer(location).data
        response_data['name'] = location.customer.name
        
        return Response(response_data)

    def perform_create(self, serializer):
        try:
            customer = CustomerAuth.objects.get(id=self.request.user.id)
        except CustomerAuth.DoesNotExist:
            raise serializers.ValidationError({'error': 'Customer not found'})
        
        if serializer.validated_data.get('is_active'):
            CustomerLocation.objects.filter(customer=customer, is_active=True).update(is_active=False)
        serializer.save(customer=customer)

    def perform_update(self, serializer):
        try:
            customer = CustomerAuth.objects.get(id=self.request.user.id)
        except CustomerAuth.DoesNotExist:
            raise serializers.ValidationError({'error': 'Customer not found'})
        
        if serializer.validated_data.get('is_active'):
            CustomerLocation.objects.filter(customer=serializer.instance.customer, is_active=True).update(is_active=False)
        serializer.save(customer=customer)


class VendorCompleteProfileViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    queryset = VendorCompleteProfile.objects.all()
    serializer_class = VendorCompleteProfileSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        data = request.data.copy()
        data['vendor'] = vendor.id
        
        try:
            vendor_complete_profile = VendorCompleteProfile.objects.get(vendor=vendor)
            # If an entry exists, update it
            serializer = self.get_serializer(vendor_complete_profile, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
        except VendorCompleteProfile.DoesNotExist:
            # If no entry exists, create a new one
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
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
        except VendorAuth.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)

        location = serializer.save(vendor=vendor)
        response_data = self.get_serializer(location).data
        response_data['id'] = vendor.id
        
        return Response(response_data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        
        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
        except VendorAuth.DoesNotExist:
            return Response({'error': 'Vendor not found'}, status=status.HTTP_404_NOT_FOUND)
        
        location = serializer.save(vendor=vendor)
        response_data = self.get_serializer(location).data
        response_data['name'] = location.vendor.user.name
        
        return Response(response_data)

    def perform_create(self, serializer):
        try:
            vendor = VendorAuth.objects.get(id=self.request.user.id)
        except VendorAuth.DoesNotExist:
            raise serializers.ValidationError({'error': 'Vendor not found'})
        
        if serializer.validated_data.get('is_active'):
            VendorLocation.objects.filter(vendor=vendor, is_active=True).update(is_active=False)
        serializer.save(vendor=vendor)

    def perform_update(self, serializer):
        try:
            vendor = VendorAuth.objects.get(id=self.request.user.id)
        except VendorAuth.DoesNotExist:
            raise serializers.ValidationError({'error': 'Vendor not found'})
        
        if serializer.validated_data.get('is_active'):
            VendorLocation.objects.filter(vendor=serializer.instance.vendor, is_active=True).update(is_active=False)
        serializer.save(vendor=vendor)


class VendorStatusUpdateViewSet(viewsets.GenericViewSet):
    queryset = VendorLocation.objects.all()
    serializer_class = VendorLocationStatusUpdateSerializer
    permission_classes = [IsAuthenticated]

    def update_status(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        is_active = serializer.validated_data['is_active']

        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            vendor_location = VendorLocation.objects.get(vendor=vendor)
            vendor_location.is_active = is_active
            vendor_location.save()
        except VendorLocation.DoesNotExist:
            return Response({"error": "Vendor location not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response({"status": "success", "data": serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        return self.update_status(request, *args, **kwargs)

class VendorProfileDetailView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        latitude = serializer.validated_data['latitude']
        longitude = serializer.validated_data['longitude']

        try:
            customer = CustomerAuth.objects.get(id=request.user.id)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        # Filter vendors where is_active is True
        active_vendors = VendorLocation.objects.filter(is_active=True)
        min_distance = float('inf')
        nearest_vendor = None

        for vendor in active_vendors:
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
                "message": "Pickup request created and assigned to the nearest active vendor",
                "pickup_request": PickupRequestSerializer(pickup_request).data,
            }, status=status.HTTP_201_CREATED)
        else:
            pickup_request = PickupRequest.objects.create(
                customer=customer,
                latitude=latitude,
                longitude=longitude,
                status='No Active Vendors Available'
            )
            return Response({"error": "No active vendors found"}, status=status.HTTP_404_NOT_FOUND)


class VendorPickupRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)

        pickup_requests = PickupRequest.objects.filter(vendor=vendor)
        if not pickup_requests.exists():
            return Response({"error": "No pickup requests found for the provided vendor"}, status=status.HTTP_404_NOT_FOUND)

        pickup_requests_data = []
        for request in pickup_requests:
            request_data = {
                "customer_id": request.customer.id,
                "customer_name": request.customer.name,
                "customer_phone_number": request.customer.phone_number,
                "latitude": request.latitude,
                "longitude": request.longitude,
                "pickup_request_id": request.id,
                "status": request.status,
                "remarks": request.remarks,  # Include remarks field
            }
            pickup_requests_data.append(request_data)

        return Response(pickup_requests_data, status=status.HTTP_200_OK)
    

class UpdatePickupRequestStatusView(generics.GenericAPIView):
    serializer_class = UpdatePickupRequestStatusSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            pickup_request_id = serializer.validated_data['pickup_request_id']
            new_status = serializer.validated_data['status']

            try:
                vendor = VendorAuth.objects.get(id=request.user.id)
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
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            customer = CustomerAuth.objects.get(id=request.user.id)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            pickup_request = PickupRequest.objects.get(customer=customer, status='Accepted')
        except PickupRequest.DoesNotExist:
            return Response({"error": "No accepted pickup requests found for the provided customer"}, status=status.HTTP_404_NOT_FOUND)

        if pickup_request.vendor is None:
            return Response({"error": "No vendor assigned to this accepted pickup request"}, status=status.HTTP_404_NOT_FOUND)

        vendor = pickup_request.vendor
        serializer = VendorDetailsSerializer(vendor)

        response_data = {
            "vendor_details": serializer.data,
            "pickup_request_id": pickup_request.id,
        }

        return Response(response_data, status=status.HTTP_200_OK)
    

class RejectAndReassignPickupRequestView(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = RejectAndReassignPickupRequestSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        pickup_request_id = serializer.validated_data['pickup_request_id']

        try:
            vendor = VendorAuth.objects.get(id=request.user.id)
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

        # Find the next nearest active vendor who has not rejected the request
        customer_location = (pickup_request.latitude, pickup_request.longitude)
        active_vendors = VendorLocation.objects.exclude(vendor__in=pickup_request.rejected_vendors.all()).filter(is_active=True)
        min_distance = float('inf')
        nearest_vendor = None

        for vendor_location in active_vendors:
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
                "message": "Pickup request reassigned to the next nearest active vendor",
                "pickup_request": PickupRequestSerializer(pickup_request).data,
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "No other active vendors available"}, status=status.HTTP_404_NOT_FOUND)
        
class CustomerRejectPickupRequestView(generics.GenericAPIView):
    serializer_class = RejectPickupRequestSerializer  
    permission_classes = [IsAuthenticated]  

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pickup_request_id = serializer.validated_data['pickup_request_id']
        remarks = serializer.validated_data.get('remarks', 'Rejected by customer')

        try:
            customer = CustomerAuth.objects.get(id=request.user.id)
        except CustomerAuth.DoesNotExist:
            return Response({"error": "Customer profile not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
            pickup_request = PickupRequest.objects.get(id=pickup_request_id, customer=customer)
        except PickupRequest.DoesNotExist:
            return Response({"error": "Pickup request not found for the provided ID and customer"}, status=status.HTTP_404_NOT_FOUND)

        if pickup_request.status != 'Accepted':
            return Response({"error": "This pickup request is not currently accepted by any vendor"}, status=status.HTTP_400_BAD_REQUEST)

        pickup_request.status = 'Rejected'
        pickup_request.remarks = remarks
        pickup_request.save()

        return Response({"message": "Pickup request rejected successfully", "pickup_request": PickupRequestSerializer(pickup_request).data}, status=status.HTTP_200_OK)