"""
Bookclub serializers: Club create/list with automatic owner membership.

When a user creates a club, they are set as created_by and we create a UserClub
row with role=owner, status=approved so there is exactly one owner per club.
"""
from rest_framework import serializers
from .models import Club, UserClub


class ClubSerializer(serializers.ModelSerializer):
    """Serialize Club for list and create. On create, creator becomes the sole owner via UserClub."""

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "description",
            "banner_image",
            "owner",
            "is_public",
            "max_members",
            "club_meeting_mode",
            "club_location",
            "created_at",
        ]
        read_only_fields = ["id", "owner", "created_at"]

    def create(self, validated_data):
        """Set creator from request and create an Owner UserClub row (one owner per club)."""
        validated_data["owner"] = self.context["request"].user
        club = super().create(validated_data)
        UserClub.objects.create(
            user=club.owner,
            club=club,
            role=UserClub.ROLE_OWNER,
            status=UserClub.STATUS_APPROVED,
        )
        return club
