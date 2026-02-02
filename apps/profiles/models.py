from django.db import models
from apps.common.models import BaseModel
from django.contrib.auth import get_user_model

User = get_user_model()


# Create your models here.
class ShippingAddress(BaseModel):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="shipping_addresses"
    )
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=12)
    address = models.CharField(max_length=1000)
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=200)
    zipcode = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.full_name}'s shipping details"
