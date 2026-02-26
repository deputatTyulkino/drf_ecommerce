from django.contrib.auth import get_user_model
from rest_framework import serializers

from apps.profiles.models import ShippingAddress

User = get_user_model()


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'avatar', 'account_type')
        read_only_fields = ('email', 'account_type')


class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = ('id', 'full_name', 'email', 'phone', 'address', 'city', 'country', 'zipcode')
        read_only_fields = ('id',)
