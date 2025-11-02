from rest_framework import serializers
from .models import ResidentProfile, User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_resident', 'is_admin']


class ResidentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ResidentProfile
        fields = ['user', 'barangay_id', 'address', 'birthdate', 'expiry_date']


class ResidentIDSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = ResidentProfile
        fields = ['username', 'barangay_id', 'date_registered', 'expiry_date']
