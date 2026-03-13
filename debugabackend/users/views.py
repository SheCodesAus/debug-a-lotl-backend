"""
User API: registration, current user profile, and token login.

Endpoints:
  POST /users/            - register a user
  GET  /users/me/         - current authenticated user profile
  PATCH /users/me/        - update current authenticated user profile
Token auth is at POST /api-token-auth/ (see project urls).
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, MeSerializer


class RegisterUser(APIView):
    """Register a new user account."""

    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class CurrentUser(APIView):
    """Get and update the currently authenticated user's profile."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = MeSerializer(request.user)
        return Response(serializer.data)

    def patch(self, request):
        serializer = MeSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CustomAuthToken(ObtainAuthToken):
    """
    Login: POST username + password; returns token and user info.

    Response includes token (use in Authorization: Token <key>) plus user_id, username,
    email, profile_picture, bio, date_joined. Rejects inactive or invalid accounts.
    """

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data,
            context={"request": request},
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        if not user.is_active:
            return Response(
                {"detail": "This account is disabled."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if not (user.username or user.username.strip()):
            return Response(
                {"detail": "Invalid account: no username."},
                status=status.HTTP_403_FORBIDDEN,
            )

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "name": user.name,
            "email": user.email or "",
            "profile_picture": user.profile_picture or "",
            "bio": user.bio or "",
            "date_joined": user.date_joined,
        })
