from django.urls import path
from . import views

# User endpoints: list/create, current user (me), and public profile by pk.
urlpatterns = [
    path("users/", views.CustomUserList.as_view()),
    path("users/me/", views.CurrentUser.as_view()),
    path("users/<int:pk>/", views.CustomUserDetail.as_view()),
]