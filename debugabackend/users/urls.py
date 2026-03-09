from django.urls import path
from . import views

# User endpoints: register and user profile by id.
urlpatterns = [
    path("users/", views.RegisterUser.as_view()),
    path("users/<int:id>/", views.CurrentUser.as_view()),
]
