from django.urls import path

from apps.sellers.views import SellerProductsView, SellersView

urlpatterns = [
    path("", SellersView.as_view()),
    path("products/", SellerProductsView.as_view()),
    path("products/<slug:slug>/", SellerProductsView.as_view()),
]
