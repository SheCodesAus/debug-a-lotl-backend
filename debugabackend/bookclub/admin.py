from django.contrib import admin
from .models import Club


@admin.register(Club)
class ClubAdmin(admin.ModelAdmin):
    list_display = ["name", "meeting_type", "is_public", "created_by", "created_at"]
    list_filter = ["is_public", "meeting_type"]
    search_fields = ["name", "description", "location"]
