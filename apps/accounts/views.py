from django.contrib.auth.password_validation import validate_password
from rest_framework.generics import CreateAPIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from apps.accounts.serializers import CreateUserSerializer
from apps.accounts.serializers import MyTokenObtainPairSerializer


# Create your views here.
class RegisterViewSet(CreateAPIView):
    serializer_class = CreateUserSerializer

    def validate_password(self, value):
        validate_password(value)
        return value

    def post(self, request, *args, **kwargs):
        super().create(request, *args, **kwargs)


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
