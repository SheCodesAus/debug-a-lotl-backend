"""
Django admin for bookclub: UserClub memberships (owner/member, status) and Club.
"""
from django.contrib import admin
from .models import Club, UserClub


@admin.register(UserClub)
class UserClubAdmin(admin.ModelAdmin):
    """Admin for user–club memberships: one owner per club (creator), others as members with status."""

    list_display = ["user", "club", "role", "status", "joined_at"]
    list_filter = ["role", "status"]
    search_fields = ["user__username", "club__name"]


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Admin for book clubs: list view, filters, and search."""

    list_display = ["name", "meeting_type", "is_public", "created_by", "created_at"]
    list_filter = ["is_public", "meeting_type"]
    search_fields = ["name", "description", "location"]
