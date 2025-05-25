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

