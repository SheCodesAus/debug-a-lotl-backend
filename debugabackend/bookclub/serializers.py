"""
Bookclub serializers: Club create/list with automatic owner membership.

When a user creates a club, they are set as created_by and we create a UserClub
row with role=owner, status=approved so there is exactly one owner per club.
"""
from rest_framework import serializers
from .models import Club, Member


class ClubSerializer(serializers.ModelSerializer):
#Show owner user name in response without allowing clients to set it

    owner_name = serializers.ReadOnlyField(source = "owner.name")

    class Meta:
        model = Club
        fields = [
            "id",
            "name",
            "description",
            "banner_image",
            "owner",
            "owner_name",
            "is_public",
            "max_members",
            "club_meeting_mode",
            "club_location",
            "created_at",
        ]
        read_only_fields = ["id","owner","owner_name", "created_at"]

    def create(self, validated_data):
        # The logged-in user becomes the club owner automatically.
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)

class MemberSerializer(serializers.ModelSerializer):
    #Expose basic user info for member list
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Member
        fields = [ "id", "user", "username", "club", "status" , "joined_at"]
        read_only_fields = ["id", "user", "username", "club", "joined_at"]