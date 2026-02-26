from rest_framework import serializers

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
