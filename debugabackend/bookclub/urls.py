from django.urls import path
from . import views

urlpatterns = [
    path("clubs/", views.ClubListCreate.as_view()),
    path("clubs/<int:pk>/", views.ClubDetail.as_view()),
    path("clubs/<int:pk>/join/", views.ClubJoinView.as_view()),
    path("clubs/<int:pk>/members/", views.ClubMembersView.as_view()),
    path(
        "clubs/<int:club_pk>/members/<int:member_pk>/",
        views.MemberStatusUpdateView.as_view(),
    ),
]
