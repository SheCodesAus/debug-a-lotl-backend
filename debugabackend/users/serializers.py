"""
User serializers for registration and profile API.

CustomUserSerializer: full profile fields; password write-only, date_joined read-only.
"""
from rest_framework import serializers
from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    """
    Serialize CustomUser for list/detail and for registration (POST).

    Exposes all model fields; password is write-only and date_joined is set by the server.
    """

    class Meta:
        model = CustomUser
        fields = '__all__'
        # Never return password in API responses.
        extra_kwargs = {'password': {'write_only': True}}
        # Set automatically on create; not editable via API.
        read_only_fields = ('date_joined',)

    def create(self, validated_data):
        """Use create_user so password is hashed correctly."""
        return CustomUser.objects.create_user(**validated_data)