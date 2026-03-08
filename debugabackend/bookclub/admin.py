"""
Django admin for bookclub: UserClub memberships (owner/member, status) and Club.
""""""
Django admin for bookclub models.
"""
from django.contrib import admin
from .models import Club, UserClub, Meeting, MeetingAttendance, ClubBook, AnnouncementThread


@admin.register(UserClub)
class UserClubAdmin(admin.ModelAdmin):
    list_display = ["user", "club", "role", "status", "joined_at"]
    list_filter = ["role", "status"]
    search_fields = ["user__username", "club__name"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_public", "max_members", "club_meeting_mode", "created_at"]
    list_filter = ["is_public", "club_meeting_mode"]
    search_fields = ["name", "description", "club_location", "owner__username"]


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", "club", "meeting_date", "start_time", "meeting_type", "created_by"]
    list_filter = ["meeting_type", "meeting_date"]
    search_fields = ["title", "description", "club__name", "location"]


@admin.register(MeetingAttendance)
class MeetingAttendanceAdmin(admin.ModelAdmin):
    list_display = ["meeting", "user", "booked_at"]
    list_filter = ["booked_at"]
    search_fields = ["meeting__title", "user__username", "meeting__club__name"]


@admin.register(ClubBook)
class ClubBookAdmin(admin.ModelAdmin):
    list_display = ["title", "club", "status", "author", "genre", "added_by", "added_at"]
    list_filter = ["status", "genre"]
    search_fields = ["title", "author", "isbn", "google_books_id", "club__name"]


@admin.register(AnnouncementThread)
class AnnouncementThreadAdmin(admin.ModelAdmin):
    list_display = ["club", "created_by", "sent_at"]
    list_filter = ["sent_at"]
    search_fields = ["club__name", "created_by__username", "message"]

from django.contrib import admin
from .models import Club, UserClub, Meeting, MeetingAttendance, ClubBook, AnnouncementThread
