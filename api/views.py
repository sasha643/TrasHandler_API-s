from django.shortcuts import render
from rest_framework import viewsets, mixins
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from .models import *
from .serializers import *

# Create your views here.

User = get_user_model()

class CustomerAuthViewSet(viewsets.GenericViewSet):
    queryset = CustomerAuth.objects.all()
    serializer_class = CustomerAuthSerializer

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

    
class VendorLocationViewSet(viewsets.GenericViewSet, mixins.CreateModelMixin):
    """
    Handle creating and updating vendor locations
    """
    permission_classes = [IsAuthenticated]
    serializer_class = VendorLocationSerializer
    queryset = VendorLocation.objects.all()

    def perform_create(self, serializer):
        # Retrieve the authenticated user
        user = self.request.user
        try:
            # Get the VendorAuth instance associated with the authenticated user
            vendor_auth = VendorAuth.objects.get(user=user)
            # Check if a VendorLocation already exists for this VendorAuth
            vendor_location = VendorLocation.objects.filter(vendor=vendor_auth).first()
            if vendor_location:
                # Update the existing VendorLocation
                serializer = self.get_serializer(vendor_location, data=self.request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(vendor=vendor_auth)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except VendorAuth.DoesNotExist:
            return Response({"error": "Vendor profile not found"}, status=status.HTTP_404_NOT_FOUND)
        except VendorLocation.DoesNotExist:
            # Create a new VendorLocation
            serializer.save(vendor=vendor_auth)
            return Response(serializer.data, status=status.HTTP_201_CREATED)