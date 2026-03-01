from rest_framework import permissions
from rest_framework.permissions import BasePermission

from apps.shop.models import Review


class IsReviewer(BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        is_review = Review.objects.filter(user=request.user, product=obj.product).exists()
        if (
                obj.user == request.user and
                request.user.is_authenticated and
                request.user.seller.account_type != 'SELLER' and
                not is_review
        ) or request.user.is_staff:
            return True
        return False
