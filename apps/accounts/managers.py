from django.contrib.auth.base_user import BaseUserManager
from django.core.validators import validate_email
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError


class CustomUserManager(BaseUserManager):
    @staticmethod
    def email_validator(email):
        try:
            validate_email(email)
        except ValidationError:
            raise ValueError("You must provide a valid email address")

    @staticmethod
    def password_validator(password):
        try:
            validate_password(password)
        except ValidationError:
            raise ValidationError("You must provide a valid password")

    def validate_user(self, first_name, last_name, email, password):
        if not first_name:
            raise ValueError("Users must submit a first name")

        if not last_name:
            raise ValueError("Users must submit a last name")

        if email:
            email = self.normalize_email(email)
            self.email_validator(email)
        else:
            raise ValueError("Base User Account: An email address is required")

        if password:
            self.password_validator(password)
        else:
            raise ValueError("Base User Account: A password is required")

    def create_user(self, first_name, last_name, email, password, **extra_fields):
        self.validate_user(
            first_name=first_name, last_name=last_name, email=email, password=password
        )
        user = self.model(
            first_name=first_name, last_name=last_name, email=email, **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    @staticmethod
    def validate_superuser(**extra_fields):
        extra_fields.setdefault("is_staff", True)
        if not extra_fields.get("is_staff"):
            raise ValueError("Superusers must have is_staff=True")
        return extra_fields

    def create_superuser(self, first_name, last_name, email, password, **extra_fields):
        extra_fields = self.validate_superuser(**extra_fields)
        user = self.create_user(first_name, last_name, email, password, **extra_fields)
        return user
