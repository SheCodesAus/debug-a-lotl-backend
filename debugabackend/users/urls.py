from django.urls import path
from . import views

# User endpoints: register and current authenticated user profile.
urlpatterns = [
    path("users/", views.RegisterUser.as_view()),
    path("users/me/", views.CurrentUser.as_view()),
]
