from django.urls import path
from .views import ClubListCreate, MeetingListCreate, AnnouncementListCreate

urlpatterns = [
    path('clubs/', ClubListCreate.as_view(), name='club-list'),
    path('clubs/<int:club_id>/meetings/', MeetingListCreate.as_view(), name='meeting-list'),
    path('clubs/<int:club_id>/announcements/', AnnouncementListCreate.as_view(), name='announcement-list'),
]
    path("clubs/", views.ClubListCreate.as_view()),
    path("clubs/<int:pk>/", views.ClubDetail.as_view()),
    path("clubs/<int:pk>/join/", views.ClubJoinView.as_view()),
    path("clubs/<int:pk>/members/", views.ClubMembersView.as_view()),
    path(
        "clubs/<int:club_pk>/members/<int:member_pk>/",
        views.MemberStatusUpdateView.as_view(),
    ),
]
