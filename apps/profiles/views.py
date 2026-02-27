from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import RetrieveUpdateDestroyAPIView, ListCreateAPIView, ListAPIView
from rest_framework.response import Response

from apps.common.permissions import IsOwner
from apps.profiles.models import ShippingAddress, Order, OrderItem
from apps.profiles.serializers import ProfileSerializer, ShippingAddressSerializer
from apps.shop.serializers import OrderSerializer, CheckItemOrderSerializer

tags = ["Profiles"]


# Create your views here.
class ProfileView(RetrieveUpdateDestroyAPIView):
    serializer_class = ProfileSerializer
    permission_classes = [IsOwner]

    def get_object(self):
        user = self.request.user
        self.check_object_permissions(self.request, user)
        return user

    @extend_schema(
        summary="Retrieve Profile",
        description='This endpoint allows a user to retrieve his/her profile.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update Profile",
        description='This endpoint allows a user to update his/her profile.',
        tags=tags,
        request={"multipart/form-data": serializer_class},
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

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
    permission_classes = [IsOwner]

    def get_queryset(self):
        return ShippingAddress.objects.filter(user=self.request.user)

    @extend_schema(
        summary="Shipping Addresses Fetch",
        description='This endpoint returns all shipping addresses associated with a user.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

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
    permission_classes = [IsOwner]

    def get_object(self):
        shipping_address = (
            ShippingAddress.objects
            .filter(user=self.request.user)
            .get_or_none(id=self.kwargs["id"])
        )
        if shipping_address is None:
            raise NotFound(detail={"message": "Shipping Address does not exist!"})
        self.check_object_permissions(self.request, shipping_address)
        return shipping_address

    @extend_schema(
        summary="Shipping Address Fetch ID",
        description='This endpoint returns a single shipping address associated with a user.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Update Shipping Address ID",
        description='This endpoint allows a user to update his/her shipping address.',
        tags=tags,
    )
    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    @extend_schema(
        summary="Delete Shipping Address ID",
        description='This endpoint allows a user to delete his/her shipping address.',
        tags=tags,
    )
    def delete(self, request, *args, **kwargs):
        super().delete(request, *args, **kwargs)


class OrdersView(ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsOwner]

    def get_queryset(self):
        return (Order.objects
                .select_related('user')
                .prefetch_related('orderitems', 'orderitems__product')
                .order_by('-created_at')
                )

    @extend_schema(
        operation_id="orders_view",
        summary="Orders Fetch",
        description='This endpoint returns all orders for a particular user.',
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class OrderItemsView(ListAPIView):
    serializer_class = CheckItemOrderSerializer
    permission_classes = [IsOwner]

    def get_order(self):
        order = Order.objects.get_or_none(tx_ref=self.kwargs['tx_ref'])
        if not order:
            return Response(data={"message": "Order does not exist!"}, status=404)
        self.check_object_permissions(self.request, order)
        return order

    def get_queryset(self):
        order = self.get_order()
        return OrderItem.select.filter(order=order)

    @extend_schema(
        operation_id="order_items_view",
        summary="Items Order Fetch",
        description='This endpoint returns all items order for a particular user.',
        tags=tags,

    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
