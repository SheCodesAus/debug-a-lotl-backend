"""Django admin for bookclub models."""
from django.contrib import admin
from .models import Club, Member, Meeting, MeetingAttendance, ClubBook, AnnouncementThread


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ["user", "club", "status", "joined_at"]
    list_filter = ["status", "joined_at"]
    search_fields = ["user__username", "user__email", "club__name"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "is_public", "max_members", "club_meeting_mode", "created_at"]
    list_filter = ["is_public", "club_meeting_mode"]
    search_fields = ["name", "description", "club_location", "owner__username", "owner__email"]


@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ["title", "club", "meeting_date", "start_time", "meeting_type", "created_at"]
    list_filter = ["meeting_type", "meeting_date"]
    search_fields = ["title", "description", "club__name", "location"]


@admin.register(MeetingAttendance)
class MeetingAttendanceAdmin(admin.ModelAdmin):
    list_display = ["meeting", "member", "booked_at"]
    list_filter = ["booked_at"]
    search_fields = [
        "meeting__title",
        "meeting__club__name",
        "member__user__username",
        "member__user__email",
    ]


@admin.register(ClubBook)
class ClubBookAdmin(admin.ModelAdmin):
    list_display = ["title", "club", "status", "author", "genre", "added_at"]
    list_filter = ["status", "genre"]
    search_fields = ["title", "author", "isbn", "google_books_id", "club__name"]


@admin.register(AnnouncementThread)
class AnnouncementThreadAdmin(admin.ModelAdmin):
    list_display = ["club", "title", "sent_at"]
    list_filter = ["sent_at"]
    search_fields = ["club__name", "title", "message"]
