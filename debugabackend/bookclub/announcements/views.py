from rest_framework import generics, permissions
from rest_framework.exceptions import NotFound
from bookclub.models import AnnouncementThread, Club  
from .serializers import AnnouncementSerializer


class IsClubOwner(permissions.BasePermission):
    def has_permission(self, request, view):
        club_id = view.kwargs.get('club_id')
        try:
            club = Club.objects.get(id=club_id)
            return club.owner == request.user
        except Club.DoesNotExist:
            return False


class AnnouncementListCreateView(generics.ListCreateAPIView):
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated(), IsClubOwner()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        club_id = self.kwargs['club_id']
        if not Club.objects.filter(id=club_id).exists():
            raise NotFound("Club not found.")
        return AnnouncementThread.objects.filter(club_id=club_id)

    def perform_create(self, serializer):
        club = Club.objects.get(id=self.kwargs['club_id'])
        serializer.save(club=club)


class AnnouncementDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AnnouncementSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAuthenticated(), IsClubOwner()]

    def get_queryset(self):
        return AnnouncementThread.objects.filter(club_id=self.kwargs['club_id'])