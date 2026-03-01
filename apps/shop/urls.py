from django.urls import path

from apps.shop.views import CategoriesView, ProductsByCategoryView, ProductsBySellerView, ProductsView, ProductView, \
    CartView, CheckoutView, ReviewView

urlpatterns = [
    path("categories/", CategoriesView.as_view()),
    path('categories/<int:pk>/', ProductsByCategoryView.as_view()),
    path('sellers/<slug:slug>/', ProductsBySellerView.as_view()),
    path('products/', ProductsView.as_view()),
    path('product/<slug:slug>/', ProductView.as_view()),
    path('cart/', CartView.as_view()),
    path('checkout/', CheckoutView.as_view()),
    path('product/<slug:slug>/reviews/', ReviewView.as_view()),
    path('product/<slug:slug>/review/', ReviewView.as_view()),
    path('product/<slug:slug>/review/<uuid:id>/', ReviewView.as_view())
]
