from drf_spectacular.utils import extend_schema
from rest_framework.exceptions import NotFound
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView

from apps.sellers.models import Seller
from apps.shop.models import Category, Product
from apps.shop.serializers import CategorySerializer, ProductSerializer

tags = ["Shop"]


class CategoriesView(ListCreateAPIView):
    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    @extend_schema(
        summary="Categories Fetch",
        description='This endpoint returns all categories.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @extend_schema(
        summary="Category Creating",
        description='This endpoint creates categories.',
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProductsByCategoryView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        category = Category.objects.get_or_none(slug=self.kwargs["slug"])
        if not category:
            return NotFound(detail={"message": "Category does not exist!"})
        return Product.objects.filter(category=category)

    @extend_schema(
        operation_id="category_products",
        summary="Category Products Fetch",
        description='This endpoint returns all products in a particular category.',
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductsView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()

    @extend_schema(
        operation_id="all_products",
        summary="Product Fetch",
        description='This endpoint returns all products.',
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductsBySellerView(ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        seller = Seller.objects.get_or_none(slug=self.kwargs["slug"])
        if not seller:
            return NotFound(detail={"message": "Seller does not exist!"})
        return Product.objects.filter(seller=seller)

    @extend_schema(
        summary="Seller Products Fetch",
        description='This endpoint returns all products in a particular seller.',
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ProductView(RetrieveAPIView):
    serializer_class = ProductSerializer

    def get_object(self):
        product = Product.objects.get_or_none(slug=self.kwargs["slug"])
        if not product:
            return NotFound(detail={"message": "Product does not exist!"})
        return product

    @extend_schema(
        operation_id="product_detail",
        summary="Product Details Fetch",
        description='This endpoint returns the details for a product via the slug.',
        tags=tags
    )
    def get(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
