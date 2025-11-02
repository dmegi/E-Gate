"""
accounts/views.py
-----------------
Handles registration, authentication, and token management
for both Resident and Admin users.

Maintainer: E-Gate Backend Team (Adamson University)
"""

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate, get_user_model
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from residents.models import ResidentProfile
from .serializers import ResidentRegisterSerializer, AdminRegisterSerializer, LoginSerializer
import logging

User = get_user_model()
logger = logging.getLogger("accounts")


# 🧩 Helper — Unified Token Response
def generate_token_response(user, message, role=None, profile_data=None):
    """
    Generates a standardized JSON response containing authentication tokens
    and user information.
    """
    refresh = RefreshToken.for_user(user)

    response = {
        "message": message,
        "tokens": {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        },
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin,
            "is_staff": user.is_staff,
            "is_resident": user.is_resident,
            "last_login": str(user.last_login) if user.last_login else None,
            "date_joined": str(user.date_joined),
        },
        "meta": {
            "role": role or "User",
            "login_time": str(timezone.now()),
        },
    }

    if profile_data:
        response["user"]["profile"] = profile_data

    return response


# 👥 Register Resident
@api_view(["POST"])
def register_resident(request):
    """
    Registers a new resident and automatically creates their profile.
    """
    serializer = ResidentRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "Resident registered successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_resident": user.is_resident,
                    "date_joined": str(user.date_joined),
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🧑‍💼 Register Admin
@api_view(["POST"])
def register_admin(request):
    """
    Registers a new admin account for system management.
    """
    serializer = AdminRegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                "message": "Admin account created successfully",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_admin": user.is_admin,
                    "is_staff": user.is_staff,
                },
            },
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 🔑 Login Resident
@api_view(["POST"])
def login_resident(request):
    """
    Authenticates a resident and returns access/refresh tokens.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]
    user = authenticate(username=username, password=password)

    if not user:
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)
    if not user.is_resident:
        return Response({"error": "Access denied: Not a resident account"}, status=status.HTTP_403_FORBIDDEN)

    # Fetch resident profile
    profile_data = None
    if hasattr(user, "profile"):
        profile = user.profile
        profile_data = {
            "barangay_id": str(profile.barangay_id),
            "address": profile.address,
            "birthdate": str(profile.birthdate),
            "date_registered": str(profile.date_registered),
            "expiry_date": str(profile.expiry_date),
        }

    response_data = generate_token_response(
        user,
        message="Resident login successful",
        role="Resident",
        profile_data=profile_data,
    )
    return Response(response_data, status=status.HTTP_200_OK)


# 🧠 Login Admin
@api_view(["POST"])
def login_admin(request):
    """
    Authenticates an admin and returns access/refresh tokens.
    """
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    username = serializer.validated_data["username"]
    password = serializer.validated_data["password"]
    user = authenticate(username=username, password=password)

    if not user:
        logger.warning(f"[FAILED ADMIN LOGIN] Username: {username}, Time: {timezone.now()}")
        return Response({"error": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

    if not user.is_admin:
        logger.warning(f"[UNAUTHORIZED ADMIN LOGIN] Username: {username}, Time: {timezone.now()}")
        return Response({"error": "Access denied: Not an admin account"}, status=status.HTTP_403_FORBIDDEN)

    logger.info(f"[ADMIN LOGIN SUCCESS] Admin: {username}, Time: {timezone.now()}")

    response_data = generate_token_response(
        user,
        message="Admin login successful",
        role="Administrator",
    )
    return Response(response_data, status=status.HTTP_200_OK)


# 🚪 Logout (Blacklist refresh token)
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout_user(request):
    """
    Blacklists the refresh token to invalidate further use.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Successfully logged out"}, status=status.HTTP_205_RESET_CONTENT)
    except Exception as e:
        logger.error(f"[LOGOUT ERROR] {str(e)}")
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
