from uuid import UUID
from rest_framework.exceptions import NotFound, ValidationError
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.views import APIView

from apps.common.utils import set_dict_attr
from apps.profiles.models import ShippingAddress
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer

tags = ["Profiles"]


# Create your views here.
class ProfileView(GenericViewSet):
    serializer_class = ProfileSerializer

    def retrieve(self, request):
        user = request.user
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = set_dict_attr(user, serializer.validated_data)
        user.save()
        serializer = self.serializer_class(user)
        return Response(serializer.data)

    def destroy(self, request):
        user = request.user
        user.is_active = False
        user.save()
        return Response(data={"message": "User Account Deactivated"})


class ShippingAddressesView(GenericViewSet):
    serializer_class = ShippingAddressSerializer

    def list(self, request):
        user = request.user
        shipping_addresses = ShippingAddress.objects.filter(user=user)
        serializer = self.serializer_class(shipping_addresses, many=True)
        return Response(serializer.data)

    def create(self, request):
        user = request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address, _ = ShippingAddress.objects.get_or_create(user=user, **data)
        serializer = self.serializer_class(shipping_address)
        return Response(serializer.data, status=201)


class ShippingAddressViewID(APIView):
    serializer_class = ShippingAddressSerializer

    def get_object(self, user, shipping_id):
        try:
            shipping_uuid = UUID(shipping_id)
        except ValueError as exc:
            raise ValidationError(
                {"message": "Invalid shipping id UUID format"}
            ) from exc

        shipping_address = ShippingAddress.objects.get_or_none(
            user=user, id=shipping_uuid
        )
        if shipping_address is None:
            raise NotFound(
                detail={"message": "Shipping Address does not exist!"}, code=404
            )

        return shipping_address

    def get(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data)

    def put(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping_address = set_dict_attr(shipping_address, data)
        shipping_address.save()
        serializer = self.serializer_class(shipping_address)
        return Response(data=serializer.data, status=200)

    def delete(self, request, *args, **kwargs):
        user = request.user
        shipping_address = self.get_object(user, kwargs["id"])
        shipping_address.delete()
        return Response(
            data={"message": "Shipping address deleted successfully"}, status=200
        )
