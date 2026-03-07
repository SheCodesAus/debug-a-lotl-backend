"""
User app models.

CustomUser extends Django's AbstractUser to match our schema:
id, username, email, password, profile_picture, bio, date_joined.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    App user: can exist without a book club; may later create one and become owner.

    Inherited from AbstractUser: id (PK), username, email, password, date_joined,
    plus is_active, is_staff, etc.
    """

    # Profile fields added for our schema (stored as URL and text).
    profile_picture = models.URLField(max_length=500, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return self.username