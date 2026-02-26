from uuid import UUID

from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView
from rest_framework.response import Response

from apps.profiles.models import ShippingAddress
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer

tags = ["Profiles"]


# Create your views here.
class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer

    def get_object(self):
        return self.request.user

    @extend_schema(
        summary="Retrieve Profile",
        description='This endpoint allows a user to retrieve his/her profile.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update Profile",
        description='This endpoint allows a user to update his/her profile.',
        tags=tags,
        request={"multipart/form-data": serializer_class},
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Deactivate account",
        description='This endpoint allows a user to deactivate his/her account.',
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response(data={"message": "User Account Deactivated"})


class ShippingAddressesView(ListCreateAPIView):
    serializer_class = ShippingAddressSerializer

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description='This endpoint returns all shipping addresses associated with a user.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create Shipping Address",
        description='This endpoint allows a user to create a shipping address.',
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, _ = ShippingAddress.objects.get_or_create(user=request.user, **data)
        serializer = self.get_serializer(shipping_address)
        return Response(data=serializer.data, status=201)


class ShippingAddressViewID(RetrieveUpdateDestroyAPIView):
    serializer_class = ShippingAddressSerializer
    lookup_field = 'id'

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    def get_object(self):
        queryset = self.get_queryset()
        shipping_address = queryset.objects.get_or_none(id=self.kwargs["id"])
        if shipping_address is None:
            raise NotFound(detail={"message": "Shipping Address does not exist!"})
        return shipping_address

    @extend_schema(
        summary="Shipping Address Fetch ID",
        description='This endpoint returns a single shipping address associated with a user.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @extend_schema(
        summary="Update Shipping Address ID",
        description='This endpoint allows a user to update his/her shipping address.',
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @extend_schema(
        summary="Delete Shipping Address ID",
        description='This endpoint allows a user to delete his/her shipping address.',
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
