"""
Bookclub models: Club and UserClub (user–club membership with role and status).

There is exactly one owner per club: the user who created it. Ownership is stored
as a UserClub row with role=owner; other users can be members (role=member) with
status pending/approved/rejected.
"""
from django.db import models
from django.conf import settings


class UserClub(models.Model):
    """
    Junction model: links a user to a club with a role and membership status.

    One owner per club (the creator); everyone else is a member. Status controls
    whether the membership is pending, approved, or rejected.
    """

    ROLE_OWNER = "owner"
    ROLE_MEMBER = "member"
    ROLE_CHOICES = [
        (ROLE_OWNER, "Owner"),
        (ROLE_MEMBER, "Member"),
    ]
    STATUS_PENDING = "pending"
    STATUS_APPROVED = "approved"
    STATUS_REJECTED = "rejected"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_APPROVED, "Approved"),
        (STATUS_REJECTED, "Rejected"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="club_memberships",
    )
    club = models.ForeignKey(
        "Club",
        on_delete=models.CASCADE,
        related_name="memberships",
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-joined_at"]
        # One membership row per user per club.
        unique_together = [["user", "club"]]
        verbose_name = "User-Club membership"

    def __str__(self):
        return f"{self.user.username} – {self.club.name} ({self.role})"


class Club(models.Model):
    """A book club. created_by is the user who created it (and the sole owner via UserClub)."""

    MEETING_IN_PERSON = "in-person"
    MEETING_VIRTUAL = "virtual"
    MEETING_CHOICES = [
        (MEETING_IN_PERSON, "In person"),
        (MEETING_VIRTUAL, "Virtual"),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField()
    banner_image = models.URLField(max_length=500, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_clubs",
    )
    current_book_id = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_public = models.BooleanField(
        default=True,
        help_text="True = public event, False = private event",
    )
    meeting_type = models.CharField(
        max_length=20,
        choices=MEETING_CHOICES,
        default=MEETING_VIRTUAL,
    )
    location = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name
