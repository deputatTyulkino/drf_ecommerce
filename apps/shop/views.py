from drf_spectacular.utils import extend_schema
from rest_framework.generics import ListCreateAPIView

from apps.shop.models import Category
from apps.shop.serializers import CategorySerializer

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
