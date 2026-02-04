from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from apps.accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        user = User(email=validated_data["email"])
        user.set_password(validated_data["password"])
        user.save()
        return user


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        if user.is_staff:
            token["group"] = "admin"
        else:
            token["group"] = "user"
            token["role"] = user.account_type
        return token
