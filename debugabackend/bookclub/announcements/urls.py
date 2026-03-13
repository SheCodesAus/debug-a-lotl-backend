from django.urls import path
from .views import AnnouncementListCreateView, AnnouncementDetailView

urlpatterns = [
    path('bookclub/<int:club_id>/announcements/', AnnouncementListCreateView.as_view()),
    path('bookclub/<int:club_id>/announcements/<int:pk>/', AnnouncementDetailView.as_view()),

]