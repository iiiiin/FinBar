from rest_framework import serializers
from .models import MarkedVideo
from django.contrib.auth import get_user_model


class MarkVideoSerializers(serializers.ModelSerializer):
    class Meta:
        model = MarkedVideo
        fields = ("id", "user_id", "videoId", "channelTitle", "title", "thumbnailURL")
        read_only_fields = (
            "id",
            "user_id",
        )

# ──────────────────────────────────────────────────────────
# 동영상 디테일용 Serializer
class YouTubeDetailSerializer(serializers.Serializer):
    id          = serializers.CharField()
    title       = serializers.CharField()
    description = serializers.CharField()
