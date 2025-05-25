from django.db import models
from django.conf import settings


# Create your models here.
class MarkedVideo(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    videoId = models.CharField(max_length=100)
    channelTitle = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    thumbnailURL = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user_id", "videoId"], name="Marked_video")
        ]
