"""
Bookclub serializers: Club create/list with automatic owner membership.

When a user creates a club, they are set as created_by and we create a UserClub
row with role=owner, status=approved so there is exactly one owner per club.
"""
from rest_framework import serializers
from .models import Club, Member, ClubBook, Meeting, MeetingAttendance, AnnouncementThread


class ClubSerializer(serializers.ModelSerializer):
#Show owner user name in response without allowing clients to set it

    owner_name = serializers.ReadOnlyField(source = "owner.name")
    member_count = serializers.SerializerMethodField()
    spots_remaining = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()

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
            "member_count",
            "spots_remaining",
            "membership_status",
            "created_at",
        ]
        read_only_fields = ["id","owner","owner_name", "member_count", "spots_remaining", "membership_status","created_at"]
    def get_membership_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        member = obj.memberships.filter(user=request.user).first()
        return member.status if member else None
    
    def get_member_count(self,obj):
        #Count approved members for private clubs
        return obj.memberships.filter(status=Member.STATUS_APPROVED).count()
    
    def get_spots_remaining(self,obj):
        #if there is no max_members limit, return none
        if obj.max_members is None:
            return None
        
        approved_count = obj.memberships.filter(
            status=Member.STATUS_APPROVED).count()
        remaining = obj.max_members - approved_count
        return max(remaining, 0)
    
    def create(self, validated_data):
        # The logged-in user becomes the club owner automatically.
        validated_data["owner"] = self.context["request"].user
        club = super().create(validated_data)

        Member.objects.create(
            user=validated_data["owner"],
            club=club,
            status=Member.STATUS_APPROVED 
        )
        return club
    
    def validate_name(self, value):
        cleaned_name = value.strip()
        # Allow updating a club without tripping the uniqueness check on itself.
        qs = Club.objects.filter(name__iexact=cleaned_name)
        if self.instance is not None:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise serializers.ValidationError("A club with this name already exists")
        return cleaned_name
    
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
        start_time = data.get("start_time", getattr(self.instance, "start_time", None))
        end_time = data.get("end_time", getattr(self.instance, "end_time", None))
        meeting_type = data.get("meeting_type", getattr(self.instance, "meeting_type", None))
        location = data.get("location", getattr(self.instance, "location", ""))
        # Move the rules here!
        
        if start_time and end_time and end_time <= start_time:
            raise serializers.ValidationError(
                {"end_time": "End time must be after start time."}
             )

        if meeting_type == "in_person" and not location:
            raise serializers.ValidationError(
                {"location": "Location required for in-person meetings."}
            )

        return data


class AnnouncementThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementThread
        fields = ['id', 'club', 'title', 'message', 'sent_at']
        read_only_fields = ['id', 'club', 'sent_at']

class ClubBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClubBook
        fields = '__all__'
        read_only_fields = ['id', 'added_at', 'club']

class MemberSerializer(serializers.ModelSerializer):
    #Expose basic user info for member list
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Member
        fields = [ "id", "user", "username", "club", "status" , "joined_at"]
        read_only_fields = ["id", "user", "username", "club", "joined_at"]

class HomeStatsSerializer(serializers.Serializer):
    active_readers = serializers.IntegerField()
    total_books_read = serializers.IntegerField()
