from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.exceptions import NotFound
from rest_framework.filters import OrderingFilter
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, CreateAPIView, GenericAPIView
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status

from apps.profiles.models import OrderItem, ShippingAddress, Order
from apps.sellers.models import Seller
from apps.shop.filter_backends import ProductsFilterBackend
from apps.shop.models import Category, Product, Review
from apps.shop.permissions import IsReviewer
from apps.shop.serializers import CategorySerializer, ProductSerializer, OrderItemSerializer, ToggleCartItemSerializer, \
    CheckoutSerializer, OrderSerializer, ReviewSerializer, CreateReviewSerializer

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
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Category Creating",
        description='This endpoint creates categories.',
        tags=tags,
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


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
        return super().get(request, *args, **kwargs)


class ProductsView(ListAPIView):
    serializer_class = ProductSerializer
    queryset = Product.select.all()
    filter_backends = [ProductsFilterBackend]

    @extend_schema(
        operation_id="all_products",
        summary="Product Fetch",
        description='This endpoint returns all products.',
        tags=tags,
        parameters=[
            OpenApiParameter(
                name="max_price",
                description="Filter products by MAX current price",
                required=False,
                type=OpenApiTypes.INT,
            ),
            OpenApiParameter(
                name="min_price",
                description="Filter products by MIN current price",
                required=False,
                type=OpenApiTypes.INT,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


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
        return super().get(request, *args, **kwargs)


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
        return super().get(request, *args, **kwargs)


class CartView(ListCreateAPIView):
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ToggleCartItemSerializer
        else:
            return OrderItemSerializer

    def get_queryset(self):
        return OrderItem.select.filter(user=self.request.user, order=None)

    def get_product(self):
        product = Product.objects.get_or_none(slug=self.kwargs["slug"])
        if not product:
            return NotFound(detail={"message": "No Product with that slug"})
        return product

    @extend_schema(
        summary="Cart Items Fetch",
        description='This endpoint returns all items in a user cart.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Toggle Item in cart",
        description="""
               This endpoint allows a user or guest to add/update/remove an item in cart.
               If quantity is 0, the item is removed from cart
           """,
        tags=tags,
        request=ToggleCartItemSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = self.get_product()
        orderitem, created = OrderItem.objects.update_or_create(
            user=user,
            order=None,
            product=product,
            defaults={'quantity': data['quantity']},
        )
        resp_message_substring = "Updated In"
        status_code = 200
        if created:
            status_code = 201
            resp_message_substring = "Added To"
        if orderitem.quantity == 0:
            resp_message_substring = "Removed From"
            orderitem.delete()
            data = None
        if resp_message_substring != "Removed From":
            serializer = self.serializer_class(orderitem)
            data = serializer.data
        return Response(
            data={"message": f"Item {resp_message_substring} Cart", "item": data},
            status=status_code
        )


class CheckoutView(CreateAPIView):
    serializer_class = CheckoutSerializer

    def get_shipping_address(self, id):
        shipping = ShippingAddress.objects.get_or_none(id=id)
        if not shipping:
            return Response({"message": "No shipping address with that ID"}, status=404)
        return shipping

    def get_orderitems(self):
        orderitems = OrderItem.objects.filter(user=self.request.user, order=None)
        if not orderitems.exists():
            return Response({"message": "No Items in Cart"}, status=404)
        return orderitems

    def create_order(self, obj):
        fields_to_update = [
            "full_name",
            "email",
            "phone",
            "address",
            "city",
            "country",
            "zipcode",
        ]
        data = {field: getattr(obj, field) for field in fields_to_update}
        return Order.objects.create(user=self.request.user, **data)

    @extend_schema(
        summary="Checkout",
        description='This endpoint allows a user to create an order through which payment can then be made through.',
        tags=tags,
        request=CheckoutSerializer,
    )
    def post(self, request, *args, **kwargs):
        orderitems = self.get_orderitems()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        shipping = self.get_shipping_address(data.get('shipping_id'))
        order = self.create_order(shipping)
        orderitems.update(order=order)
        serializer = OrderSerializer(order)
        return Response(
            data={"message": "Checkout Successful", "item": serializer.data}, status=200
        )


class ReviewView(DestroyModelMixin, ListCreateAPIView):
    permission_classes = [IsReviewer]
    lookup_field = 'id'
    filter_backends = [OrderingFilter]
    ordering_param = 'sort'
    ordering_fields = ['created_at', 'rating']

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ReviewSerializer
        else:
            return CreateReviewSerializer

    def get_product(self):
        product = Product.objects.get_or_none(slug=self.kwargs['slug'])
        if not product:
            raise NotFound("No Product with that slug")
        return product

    def get_reviews(self, product):
        user = self.request.user
        reviews = Review.objects.filter(user=user, product=product)
        if not reviews.exists():
            return Response(data={'message': "No Reviews"}, status=status.HTTP_404_NOT_FOUND)
        return reviews

    def get_queryset(self):
        product = self.get_product()
        reviews = self.get_reviews(product)
        return reviews

    @extend_schema(
        summary="Reviews Fetch",
        description='This endpoint returns all reviews of product.',
        tags=tags,
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @extend_schema(
        summary="Endpoint to create or update a review of product",
        description='This endpoint create a new review for product',
        tags=tags,
        request=CreateReviewSerializer,
    )
    def post(self, request, *args, **kwargs):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        product = self.get_product()
        review, created = Review.objects.update_or_create(
            user=user,
            product=product,
            defaults=data
        )
        self.check_object_permissions(self.request, review)
        response_message = 'Updated Review'
        status_code = status.HTTP_200_OK
        if created:
            response_message = 'Created Review'
            status_code = status.HTTP_201_CREATED
            serializer = self.get_serializer(review)
            data = serializer.data
        return Response(
            data={'message': response_message, "review": data},
            status=status_code
        )

    @extend_schema(
        summary="Delete Reviews",
        description='This endpoint delete review of product.',
        tags=tags,
    )
    def destroy(self, request, *args, **kwargs):
        review = self.get_object()
        review.hard_delete()
        return Response(
            data={"message": "Success delete review"},
            status=status.HTTP_200_OK
        )
