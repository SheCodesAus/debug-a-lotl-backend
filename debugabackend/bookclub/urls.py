from django.urls import path
from . import views

urlpatterns = [
    path("clubs/", views.ClubListCreate.as_view()),
    path("books/search/", views.BookSearch.as_view()),
]
