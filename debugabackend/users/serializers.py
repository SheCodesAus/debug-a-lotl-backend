"""
User serializers for registration and private profile API.
"""
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for account registration."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "password",
            "profile_picture",
            "bio",
            "date_joined",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }
        read_only_fields = ["id", "date_joined"]

    def create(self, validated_data):
        """Use create_user so password is hashed correctly."""
        return CustomUser.objects.create_user(**validated_data)


class MeSerializer(serializers.ModelSerializer):
    """Serializer for authenticated user's own profile."""

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "profile_picture",
            "bio",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]
