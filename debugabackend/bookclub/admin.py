from django.contrib import admin
from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    """Admin for book clubs: list view, filters, and search."""

    # Columns shown in the change list.
    list_display = ["name", "meeting_type", "is_public", "created_by", "created_at"]
    # Sidebar filters for quick filtering.
    list_filter = ["is_public", "meeting_type"]
    # Search box runs against these fields.
    search_fields = ["name", "description", "location"]
