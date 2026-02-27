from django.db import models


class OrderItemManager(models.Manager):
    def get_queryset(self):
        return (super()
                .get_queryset()
                .select_related('product', 'product__seller', 'product__seller__user')
                )
