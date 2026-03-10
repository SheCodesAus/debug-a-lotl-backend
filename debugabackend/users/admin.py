"""Django admin for CustomUser."""
from django.contrib import admin
from users.models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "name", "email", "date_joined")
    search_fields = ("username", "name", "email")
    list_filter = ("date_joined", "is_active", "is_staff")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Profile", {"fields": ("name", "profile_picture", "bio")}),
        ("Contact", {"fields": ("email",)}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
