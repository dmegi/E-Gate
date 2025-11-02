from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import date, timedelta
from .models import User, ResidentProfile
from .serializers import ResidentProfileSerializer, ResidentIDSerializer


# 🧍 Register a new resident
@api_view(['POST'])
@permission_classes([AllowAny])
def register_resident(request):
    data = request.data
    try:
        username = data.get('username')
        password = data.get('password')
        address = data.get('address')
        birthdate = data.get('birthdate')

        if not username or not password:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create(
            username=username,
            password=make_password(password),
            is_resident=True
        )

        resident = ResidentProfile.objects.create(
            user=user,
            address=address,
            birthdate=birthdate,
            expiry_date=date.today() + timedelta(days=365)
        )

        serializer = ResidentProfileSerializer(resident)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


# 🔐 Resident Login
@api_view(['POST'])
@permission_classes([AllowAny])
def login_resident(request):
    username = request.data.get('username')
    password = request.data.get('password')

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)
    return Response({
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    })


# 👤 Resident profile
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resident_profile(request):
    user = request.user
    if not hasattr(user, 'profile'):
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ResidentProfileSerializer(user.profile)
    return Response(serializer.data)


# 🪪 Virtual Barangay ID
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def resident_virtual_id(request):
    user = request.user
    if not hasattr(user, 'profile'):
        return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

    serializer = ResidentIDSerializer(user.profile)
    return Response(serializer.data)
