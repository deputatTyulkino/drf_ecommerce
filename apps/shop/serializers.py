from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from apps.profiles.models import OrderItem, Order
from apps.profiles.serializers import ShippingAddressSerializer
from apps.sellers.models import Seller
from apps.shop.models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ('slug',)


class SellerShopSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="business_name")
    avatar = serializers.CharField(source="user.avatar")

    class Meta:
        model = Seller
        fields = ('name', 'slug', 'avatar')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class CreateProductSerializer(serializers.ModelSerializer):
    category_slug = serializers.SlugField(source="category.slug")

    class Meta:
        model = Product
        fields = (
            'name',
            'desc',
            'price_current',
            'category_slug',
            'is_stock',
            'image1',
            'image2',
            'image3'
        )


class OrderItemProductSerializer(serializers.ModelSerializer):
    seller = SellerShopSerializer()
    price = serializers.DecimalField(max_digits=10, decimal_places=2, source='price_current')

    class Meta:
        model = Product
        fields = ('seller', 'name', 'slug', 'price')


class OrderItemSerializer(serializers.ModelSerializer):
    product = OrderItemProductSerializer()
    total = serializers.DecimalField(max_digits=10, decimal_places=2, source="get_total")

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'total')


class ToggleCartItemSerializer(serializers.Serializer):
    slug = serializers.SlugField()
    quantity = serializers.IntegerField(min_value=0)


class CheckoutSerializer(serializers.Serializer):
    shipping_id = serializers.UUIDField


class OrderSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')
    email = serializers.EmailField(source='user.email')
    shipping_details = serializers.SerializerMethodField()
    subtotal = serializers.DecimalField(
        max_digits=100, decimal_places=2, source='get_cart_subtotal'
    )
    total = serializers.DecimalField(
        max_digits=100, decimal_places=2, source='get_cart_total'
    )

    @extend_schema_field(ShippingAddressSerializer)
    def get_shipping_details(self, obj):
        return ShippingAddressSerializer(obj).data

    class Meta:
        model = Order
        fields = (
            'tx_ref',
            'first_name',
            'last_name',
            'email',
            'shipping_details',
            'subtotal',
            'total'
        )


class CheckItemOrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer()
    total = serializers.FloatField(source='get_total')

    class Meta:
        model = OrderItem
        fields = ('product', 'quantity', 'total')
