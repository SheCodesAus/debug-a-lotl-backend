from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q
from .models import Meeting, AnnouncementThread, Club
from .serializers import ClubSerializer, MeetingSerializer, AnnouncementThreadSerializer
from .permissions import IsOwnerOrReadOnly


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
    
class MeetingListCreate(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, club_id):
        meetings = Meeting.objects.filter(club_id=club_id)
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)

    def post(self, request, club_id):
        club = Club.objects.get(pk=club_id)
        # Check if user is owner before allowing meeting creation
        if club.owner != request.user:
            return Response({"detail": "Only the owner can create meetings."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = MeetingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club) # Automatically link to the club
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AnnouncementListCreate(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get(self, request, club_id):
        announcements = AnnouncementThread.objects.filter(club_id=club_id)
        serializer = AnnouncementThreadSerializer(announcements, many=True)
        return Response(serializer.data)

    def post(self, request, club_id):
        club = Club.objects.get(pk=club_id)
        # Check if the person posting is the owner
        if club.owner != request.user:
            return Response({"detail": "Only the owner can post announcements."}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = AnnouncementThreadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(club=club)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
