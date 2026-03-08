from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q

from .models import Club
from .serializers import ClubSerializer


class ClubListCreate(APIView):
    def get_permissions(self):
        if self.request.method == "POST":
            return [IsAuthenticated()]
        return [AllowAny()]

    def get(self, request):
        if request.user.is_authenticated:
        # Show public clubs + clubs where user is owner/member
            clubs = Club.objects.filter(
                Q(is_public=True) |
                Q(owner=request.user) |
                Q(memberships__user=request.user, memberships__status="approved")
            ).distinct()
        else:
            # Anonymous users only see public clubs
            clubs = Club.objects.filter(is_public=True)

        serializer = ClubSerializer(clubs, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ClubSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
