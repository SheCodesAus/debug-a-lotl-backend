from django.urls import path
from . import views
from .announcements.views import AnnouncementListCreateView, AnnouncementDetailView

urlpatterns = [

    # Clubs
    path("clubs/", views.ClubListCreate.as_view()),
    path("clubs/<int:pk>/", views.ClubDetail.as_view()),

    # Members
    path("clubs/<int:pk>/join/", views.ClubJoinView.as_view()),
    path("clubs/<int:pk>/members/", views.ClubMembersView.as_view()),
    path("clubs/<int:club_pk>/members/<int:member_pk>/", views.MemberStatusUpdateView.as_view()),

    # Meetings
    path("clubs/<int:club_id>/meetings/", views.MeetingListCreate.as_view()),

    # Announcements
    path("clubs/<int:club_id>/announcements/", AnnouncementListCreateView.as_view()),
    path("clubs/<int:club_id>/announcements/<int:pk>/", AnnouncementDetailView.as_view()),
]