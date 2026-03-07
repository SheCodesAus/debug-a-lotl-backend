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
            "created_by",
            "current_book_id",
            "created_at",
            "is_public",
            "meeting_type",
            "location",
        ]
        read_only_fields = ["id", "created_by", "created_at"]

    def validate(self, data):
        """Require location when meeting type is in-person."""
        if data.get("meeting_type") == Club.MEETING_IN_PERSON:
            if not (data.get("location") or "").strip():
                raise serializers.ValidationError(
                    {"location": "Location is required when the club meets in person."}
                )
        return data

    def create(self, validated_data):
        """Set creator from request and create an Owner UserClub row (one owner per club)."""
        validated_data["created_by"] = self.context["request"].user
        club = super().create(validated_data)
        UserClub.objects.create(
            user=club.created_by,
            club=club,
            role=UserClub.ROLE_OWNER,
            status=UserClub.STATUS_APPROVED,
        )
        return club
