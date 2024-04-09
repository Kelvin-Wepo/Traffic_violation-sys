from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role', 'profile_picture', 'phone_number', 'address', 'emergency_contact', 'license_plate_number', 'last_login']
