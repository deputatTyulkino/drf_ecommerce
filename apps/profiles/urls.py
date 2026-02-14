from django.urls import path

from apps.profiles.views import (
    ProfileView,
    ShippingAddressesView,
    ShippingAddressViewID,
)


urlpatterns = [
    path(
        "",
        ProfileView.as_view({"get": "retrieve", "put": "update", "delete": "destroy"}),
    ),
    path(
        "shipping_addresses/",
        ShippingAddressesView.as_view({"get": "list", "post": "create"}),
    ),
    path("shipping_addresses/detail/<str:id>/", ShippingAddressViewID.as_view()),
]
