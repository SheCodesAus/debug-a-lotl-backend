"""
Bookclub models: Club and UserClub (user–club membership with role and status).

There is exactly one owner per club: the user who created it. Ownership is stored
as a UserClub row with role=owner; other users can be members (role=member) with
status pending/approved/rejected.
"""
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.db.models import Q




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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-joined_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "club"], name="unique_user_per_club"),
            # Enforce exactly one owner row per club
            models.UniqueConstraint(
                fields=["club"],
                condition=Q(role = "owner"),
                name="unique_owner_per_club",
            ),
        ]
    def __str__(self):
        return f"{self.user.username} - {self.club.name} ({self.role}/{self.status})"

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
class Club(models.Model):
    """A book club. owner is the user who created it (and the sole owner via UserClub)."""
    MODE_VIRTUAL = "virtual"
    MODE_IN_PERSON = "in_person"
    MODE_CHOICES = [(MODE_VIRTUAL, "Virtual"), (MODE_IN_PERSON, "In person")]   

    name = models.CharField(max_length=255)
    description = models.TextField()
    banner_image = models.URLField(max_length=500, blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="owned_clubs")
    is_public = models.BooleanField(
        default=True,
        help_text="True = public event, False = private event",
    )
    max_members = models.PositiveIntegerField(null=True, blank=True)
    club_meeting_mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_VIRTUAL)
    club_location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def clean(self):
        # If the club default mode is in-person, require a default location.
        if self.club_meeting_mode == self.MODE_IN_PERSON and not self.club_location.strip():
            raise ValidationError({"club_location": "Location is required for in-person clubs."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Meeting(models.Model):
    TYPE_VIRTUAL = "virtual"
    TYPE_IN_PERSON = "in_person"
    TYPE_CHOICES = [(TYPE_VIRTUAL, "Virtual"), (TYPE_IN_PERSON, "In person")]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="meetings")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="created_meetings")
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    meeting_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    length_minutes = models.PositiveIntegerField()
    meeting_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default=TYPE_VIRTUAL)
    location = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["meeting_date", "start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": "end_time must be after start_time."})
        if self.meeting_type == self.TYPE_IN_PERSON and not self.location.strip():
            raise ValidationError({"location": "Location is required for in-person meetings."})

        # Auto-calc length from start/end if not provided or mismatched.
        start_dt = timezone.datetime.combine(self.meeting_date, self.start_time)
        end_dt = timezone.datetime.combine(self.meeting_date, self.end_time)
        self.length_minutes = int((end_dt - start_dt).total_seconds() // 60)

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
class MeetingAttendance(models.Model):
    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, related_name="attendance")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="meeting_bookings")
    booked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["meeting", "user"], name="unique_booking_per_meeting_user")
        ]

class ClubBook(models.Model):
    STATUS_TO_READ = "to_read"
    STATUS_READING = "reading"
    STATUS_READ = "read"
    STATUS_CHOICES = [
        (STATUS_TO_READ, "To Read"),
        (STATUS_READING, "Reading"),
        (STATUS_READ, "Read"),
    ]

    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="club_books")
    added_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="club_books_added")
    google_books_id = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image= models.URLField(max_length=500, blank=True)
    author = models.CharField(max_length=255, blank=True)
    isbn = models.CharField(max_length=30, blank=True)
    genre = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_TO_READ)
    start_date = models.DateField(null=True, blank=True)
    finish_date = models.DateField(null=True, blank=True)
    added_at = models.DateTimeField(auto_now_add=True)


class AnnouncementThread(models.Model):
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name="announcements")
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="announcements_created")
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
