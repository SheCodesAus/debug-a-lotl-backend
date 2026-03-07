from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """User model matching schema: id, username, email, password, profile_picture, bio, date_joined."""

    profile_picture = models.URLField(max_length=500, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username