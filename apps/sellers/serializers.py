from rest_framework import serializers

from apps.sellers.models import Seller


class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        exclude = ('user',)
        read_only_fields = ('slug', 'is_approved')
        extra_kwargs = {
            'website_url': {
                'required': False,
                'allow_null': True,
            }
        }
