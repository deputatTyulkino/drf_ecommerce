# Create your views here.
from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.generics import GenericAPIView, CreateAPIView, ListCreateAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response

from apps.sellers.models import Seller
from apps.sellers.serializers import SellerSerializer
from apps.shop.models import Category, Product
from apps.shop.serializers import ProductSerializer, CreateProductSerializer

tags = ["Sellers"]


class SellersView(CreateAPIView):
    serializer_class = SellerSerializer

    @extend_schema(
        summary="Apply to become a seller",
        description='This endpoint allows a buyer to apply to become a seller.',
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        seller, _ = Seller.objects.update_or_create(user=user, defaults=data)
        user.account_type = "SELLER"
        user.save()
        serializer = self.get_serializer(seller)
        return Response(data=serializer.data, status=201)


class SellerProductsView(ListCreateAPIView):
    serializer_class = ProductSerializer

    def get_seller(self):
        seller = Seller.objects.get_or_none(user=self.request.user, is_approved=True)
        if not seller:
            return NotFound(detail={"message": "Access is denied"})
        return seller

    def get_queryset(self):
        return Product.objects.filter(seller=self.get_object())

    def get_category(self, category_slug):
        category = Category.objects.get_or_none(slug=category_slug)
        if not category:
            return Response(
                data={"message": "Category does not exist!"}, status=404
            )
        return category

    @extend_schema(
        summary="Seller Products Fetch",
        description="""
            This endpoint returns all products from a seller.
            Products can be filtered by name, sizes or colors.
        """,
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Create a product",
        description='This endpoint allows a seller to create a product.',
        tags=tags,
        request=CreateProductSerializer,
        responses=ProductSerializer,
    )
    def post(self, request, *args, **kwargs):
        serializer = CreateProductSerializer(data=request.data)
        seller = self.get_seller()
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        category_slug = data.pop("category_slug", None)
        category = self.get_category(category_slug)
        data["category"] = category
        data["seller"] = seller
        new_prod = Product.objects.create(**data)
        serializer = ProductSerializer(new_prod)
        return Response(serializer.data, status=201)


class SellerProductView(UpdateModelMixin, DestroyModelMixin, GenericAPIView):
    serializer_class = CreateProductSerializer

    def get_object(self):
        product = Product.objects.get_or_none(slug=self.kwargs["slug"])
        seller = Seller.objects.get_or_none(user=self.request.user, is_approved=True)
        if not seller:
            return PermissionDenied(detail={"message": "Access is denied"})
        if not product:
            return NotFound(detail={"message": "Product does not exist!"})
        return product

    @extend_schema(
        summary="Seller Products Update",
        description='This endpoint updates a seller product.',
        tags=tags
    )
    def put(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)
