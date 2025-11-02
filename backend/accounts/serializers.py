"""
accounts/serializers.py
-----------------------
This module defines serializers for user registration and authentication
with a clear separation between Resident and Admin logic.

Maintainer: E-Gate Backend Team (Adamson University)
"""

from datetime import date, timedelta
from rest_framework import serializers
from django.contrib.auth import get_user_model
from residents.models import ResidentProfile

User = get_user_model()


# 👤 Resident Registration Serializer
class ResidentRegisterSerializer(serializers.ModelSerializer):
    """
    Handles resident account creation together with ResidentProfile.
    """
    address = serializers.CharField(required=True)
    birthdate = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = ["username", "password", "email", "address", "birthdate"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        # Extract related ResidentProfile data
        address = validated_data.pop("address")
        birthdate = validated_data.pop("birthdate")

        # Create resident user
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            is_resident=True,
        )

        # Auto-generate resident profile with 1-year validity
        ResidentProfile.objects.create(
            user=user,
            address=address,
            birthdate=birthdate,
            date_registered=date.today(),
            expiry_date=date.today() + timedelta(days=365),
        )

        return user


# 🧑‍💼 Admin Registration Serializer
class AdminRegisterSerializer(serializers.ModelSerializer):
    """
    Handles admin account creation with elevated permissions.
    """

    class Meta:
        model = User
        fields = ["username", "password", "email"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": False, "allow_blank": True},
        }

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            is_admin=True,
            is_staff=True,
            is_superuser=False,  # keep limited to E-Gate, not Django admin site
        )


# 🔐 Login Serializer (shared by both Resident and Admin)
class LoginSerializer(serializers.Serializer):
    """
    Basic login input validation for username/password.
    """
    username = serializers.CharField(required=True)
    password = serializers.CharField(write_only=True, required=True)
