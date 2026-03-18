from django.urls import path
from . import views

urlpatterns = [
    path("books/search/", views.BookSearch.as_view()),
    path('clubs/', views.ClubListCreate.as_view(), name='club-list'),
    path("clubs/<int:pk>/", views.ClubDetail.as_view()),
    path("clubs/<int:pk>/join/", views.ClubJoinView.as_view()),
    path("clubs/<int:pk>/members/", views.ClubMembersView.as_view()),
    path("clubs/<int:club_pk>/members/<int:member_pk>/",views.MemberStatusUpdateView.as_view(),),
    path('clubs/<int:club_id>/meetings/', views.MeetingListCreate.as_view(), name='meeting-list'),
    path( "clubs/<int:club_id>/meetings/<int:meeting_id>/", views.MeetingDetailView.as_view(),name="meeting-detail",),
    path('meetings/<int:meeting_id>/attend/', views.MeetingAttendanceView.as_view(), name='attend-meeting'),
    path('clubs/<int:club_id>/announcements/', views.AnnouncementListCreate.as_view(), name='announcement-list'),
    path("clubs/<int:club_id>/announcements/<int:announcementthread_id>/", views.AnnouncementDetailView.as_view(), name="announcement-detail",),
    path("clubs/<int:club_id>/books/", views.ClubBookListCreateView.as_view(), name="clubbook-list"),
    path("clubs/<int:club_id>/books/<int:book_id>/", views.ClubBookDetailView.as_view(), name="clubbook-detail"),
    path("stats/home/", views.HomeStatsView.as_view(), name="home-stats"),
]
