"""
Bookclub serializers: Club create/list with automatic owner membership.

When a user creates a club, they are set as created_by and we create a UserClub
row with role=owner, status=approved so there is exactly one owner per club.
"""
from rest_framework import serializers
from .models import Club, Member, ClubBook, Meeting, MeetingAttendance, AnnouncementThread


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
        read_only_fields = ["id","owner", "created_at"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
    

class MeetingAttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = MeetingAttendance
        fields = ['id', 'meeting', 'member', 'booked_at']
        read_only_fields = ['id', 'booked_at']

    def validate(self, data):
        # Prevent double boking
        if MeetingAttendance.objects.filter(meeting=data['meeting'], member=data['member']).exists():
            raise serializers.ValidationError("This member is already booked for this meeting.")
        return data
    
class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'club']

    def validate(self, data):
        # Move the rules here!
        if data.get('end_time') <= data.get('start_time'):
            raise serializers.ValidationError({"end_time": "End time must be after start time."})
        
        if data.get('meeting_type') == 'in_person' and not data.get('location'):
            raise serializers.ValidationError({"location": "Location required for in-person meetings."})
        return data


class AnnouncementThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementThread
        fields = ['id', 'club', 'title', 'message', 'sent_at']
        read_only_fields = ['id', 'sent_at']

class ClubBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubBook
        fields = '__all__'
        read_only_fields = ['id', 'added_at', 'club']

class UserClubSerializer(serializers.ModelSerializer):
    # We include 'user' and 'club' details so the frontend knows who/what this is
    username = serializers.ReadOnlyField(source='user.username')
    club_name = serializers.ReadOnlyField(source='club.name')

    class Meta:
        model = Member
        fields = ['id', 'user', 'username', 'club', 'club_name', 'status', 'joined_at']
        read_only_fields = ['id', 'joined_at', 'user', 'club']





