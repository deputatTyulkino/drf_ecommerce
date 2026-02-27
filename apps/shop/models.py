from autoslug import AutoSlugField
from django.db import models

from apps.common.models import BaseModel, IsDeletedModel
from apps.profiles.manages import OrderItemManager
from apps.sellers.models import Seller
from apps.shop.managers import ProductManager


# Create your models here.
class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    slug = AutoSlugField(populate_from="name", always_update=True, unique=True)
    image = models.ImageField(upload_to="category_images/")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"


class Product(IsDeletedModel):
    seller = models.ForeignKey(
        Seller, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    name = models.CharField(max_length=100)
    slug = AutoSlugField(populate_from="name", always_update=True, db_index=True)
    desc = models.TextField()
    price_old = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    price_current = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="products"
    )

    is_stock = models.IntegerField(default=5)

    objects = models.Manager()
    select = ProductManager()

    image1 = models.ImageField(upload_to="product_images/")
    image2 = models.ImageField(upload_to="product_images/", blank=True)
    image3 = models.ImageField(upload_to="product_images/", blank=True)

    def __str__(self):
        return self.name
