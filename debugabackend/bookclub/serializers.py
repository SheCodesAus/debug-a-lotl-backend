from rest_framework import serializers
from .models import Club


class ClubSerializer(serializers.ModelSerializer):
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
        if data.get("meeting_type") == Club.MEETING_IN_PERSON:
            if not (data.get("location") or "").strip():
                raise serializers.ValidationError(
                    {"location": "Location is required when the club meets in person."}
                )
        return data

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)
