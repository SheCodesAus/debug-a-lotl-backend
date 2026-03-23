"""
Bookclub serializers: Club create/list with automatic owner membership.

When a user creates a club, they are set as created_by and we create a UserClub
row with role=owner, status=approved so there is exactly one owner per club.
"""
from django.utils import timezone
from rest_framework import serializers
from .models import Club, Member, ClubBook, Meeting, MeetingAttendance, AnnouncementThread


class ClubSerializer(serializers.ModelSerializer):
#Show owner user name in response without allowing clients to set it

    owner_name = serializers.ReadOnlyField(source = "owner.name")
    member_count = serializers.SerializerMethodField()
    spots_remaining = serializers.SerializerMethodField()
    membership_status = serializers.SerializerMethodField()

    def _approved_members_qs(self, obj):
        return obj.memberships.filter(status=Member.STATUS_APPROVED).exclude(user=obj.owner)

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
            "is_active"
        ]
        read_only_fields = ["id","owner","owner_name", "member_count", "spots_remaining", "membership_status","created_at"]
    def get_membership_status(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return None
        member = obj.memberships.filter(user=request.user).first()
        return member.status if member else None
    
    def get_member_count(self, obj):
        # Count approved non-owner members.
        return self._approved_members_qs(obj).count()
    
    def get_spots_remaining(self,obj):
        # If there is no max_members limit, return none.
        if obj.max_members is None:
            return None

        approved_count = self._approved_members_qs(obj).count()
        remaining = obj.max_members - approved_count
        return max(remaining, 0)
    
    def validate(self, attrs):
        """Public clubs cannot enforce a max member limit."""
        instance = self.instance
        is_public = attrs.get("is_public", instance.is_public if instance else True)
        if is_public:
            attrs["max_members"] = None
        return attrs

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
    """Includes `user_has_booked` when `context[\"request\"]` is set (e.g. club meeting list)."""

    user_has_booked = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = [
            "id",
            "club",
            "title",
            "description",
            "meeting_date",
            "start_time",
            "end_time",
            "meeting_type",
            "location",
            "created_at",
            "user_has_booked",
        ]
        read_only_fields = ["id", "created_at", "club", "user_has_booked"]

    def get_user_has_booked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        if obj.club.owner_id == request.user.id:
            return False
        return MeetingAttendance.objects.filter(
            meeting=obj,
            member__user=request.user,
        ).exists()

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


class BookedMeetingClubSerializer(serializers.ModelSerializer):
    class Meta:
        model = Club
        fields = ["id", "name"]


class BookedMeetingSerializer(serializers.ModelSerializer):
    """Meeting + club summary for the current user's booked upcoming meetings."""

    club = BookedMeetingClubSerializer(read_only=True)

    class Meta:
        model = Meeting
        fields = [
            "id",
            "title",
            "meeting_date",
            "start_time",
            "end_time",
            "meeting_type",
            "location",
            "club",
        ]


class AnnouncementThreadSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementThread
        fields = ['id', 'club', 'title', 'message', 'sent_at']
        read_only_fields = ['id', 'club', 'sent_at']

class ClubBookSerializer(serializers.ModelSerializer):

    def validate(self, data):
        club = self.context.get("club")
        google_books_id = data.get("google_books_id") or getattr(self.instance, "google_books_id", "")

        if club and google_books_id:
            qs = ClubBook.objects.filter(club=club, google_books_id=google_books_id)

            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)

            if qs.exists():
                raise serializers.ValidationError(
                    {"google_books_id": "This book has already been added to this club."}
                )

        return data

    def create(self, validated_data):
        if validated_data.get("status") == ClubBook.STATUS_READ:
            validated_data.setdefault("read_at", timezone.now())
        return super().create(validated_data)

    def update(self, instance, validated_data):
        new_status = validated_data.get("status", instance.status)
        if new_status == ClubBook.STATUS_READ and instance.status != ClubBook.STATUS_READ:
            validated_data.setdefault("read_at", timezone.now())
        return super().update(instance, validated_data)

    class Meta:
        model = ClubBook
        fields = '__all__'
        read_only_fields = ['id', 'added_at', 'read_at', 'club']

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
