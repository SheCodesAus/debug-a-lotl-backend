from rest_framework import serializers
from bookclub.models import AnnouncementThread  # ← corregido

class AnnouncementSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnnouncementThread
        fields = ['id', 'club', 'title', 'message', 'sent_at']
        read_only_fields = ['sent_at', 'club']