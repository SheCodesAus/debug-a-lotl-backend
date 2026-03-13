from django.urls import path
from . import views

urlpatterns = [
    path('clubs/', views.ClubListCreate.as_view(), name='club-list'),
    path('clubs/<int:club_id>/meetings/', views.MeetingListCreate.as_view(), name='meeting-list'),
    path('clubs/<int:club_id>/announcements/', views.AnnouncementListCreate.as_view(), name='announcement-list'),
    path("clubs/<int:pk>/", views.ClubDetail.as_view()),
    path("clubs/<int:pk>/join/", views.ClubJoinView.as_view()),
    path("clubs/<int:pk>/members/", views.ClubMembersView.as_view()),
    path(
        "clubs/<int:club_pk>/members/<int:member_pk>/",
        views.MemberStatusUpdateView.as_view(),),
    path('meetings/<int:meeting_id>/attend/', views.MeetingAttendanceView.as_view(), name='attend-meeting')
]
