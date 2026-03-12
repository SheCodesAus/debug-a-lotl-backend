from django.urls import path
from .views import ClubListCreate, MeetingListCreate, AnnouncementListCreate

urlpatterns = [
    path('clubs/', ClubListCreate.as_view(), name='club-list'),
    path('clubs/<int:club_id>/meetings/', MeetingListCreate.as_view(), name='meeting-list'),
    path('clubs/<int:club_id>/announcements/', AnnouncementListCreate.as_view(), name='announcement-list'),
]