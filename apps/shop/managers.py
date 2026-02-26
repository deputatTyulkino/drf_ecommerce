from django.db import models


class ProductManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("category", "seller", "seller__user")
