"""
User API: current user, list/create, detail, and token login.

Endpoints:
  GET/POST /users/         – list all users, create (register) a user
  GET      /users/me/      – current authenticated user (requires token)
  GET      /users/<pk>/    – public profile for a user by id
Token auth is at POST /api-token-auth/ (see project urls).
"""
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .models import CustomUser
from .serializers import CustomUserSerializer


class CurrentUser(APIView):
    """Return the currently authenticated user's profile (id, username, email, profile_picture, bio, date_joined)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "id": request.user.id,
            "username": request.user.username,
            "email": request.user.email or "",
            "profile_picture": request.user.profile_picture or "",
            "bio": request.user.bio or "",
            "date_joined": request.user.date_joined,
        })


class CustomUserList(APIView):
    """List all users (GET) or register a new user (POST). No auth required for list/create."""

    def get(self, request):
        users = CustomUser.objects.all()
        serializer = CustomUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CustomUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class CustomUserDetail(APIView):
    """Public profile for a single user by primary key (read-only)."""

    def get_object(self, pk):
        try:
            return CustomUser.objects.get(pk=pk)
        except CustomUser.DoesNotExist:
            raise Http404

    def get(self, request, pk):
        user = self.get_object(pk)
        serializer = CustomUserSerializer(user)
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

        # Block disabled or invalid accounts.
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

        token, created = Token.objects.get_or_create(user=user)
        return Response({
            "token": token.key,
            "user_id": user.id,
            "username": user.username,
            "email": user.email or "",
            "profile_picture": user.profile_picture or "",
            "bio": user.bio or "",
            "date_joined": user.date_joined,
        })