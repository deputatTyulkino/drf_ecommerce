from rest_framework import status
from rest_framework.filters import BaseFilterBackend
from rest_framework.response import Response


class ProductsFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        products = queryset
        max_price_str = request.query_params.get('max_price')
        min_price_str = request.query_params.get('min_price')

        try:
            max_price = int(max_price_str)
            min_price = int(min_price_str)
        except (ValueError, TypeError):
            return Response(
                data={"message": "min_price и max_price должны быть целыми числами"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if max_price and min_price:
            if max_price <= min_price:
                return Response(
                    data={"message": "Максимальная цена должна быть больше минимальной"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if max_price:
            products = queryset.filter(price_current__lte=max_price)
        if min_price:
            products = queryset.filter(price_current__gte=min_price)
        return products
