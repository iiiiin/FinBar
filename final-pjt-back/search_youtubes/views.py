import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import MarkedVideo
from django.contrib.auth import get_user_model
from .serializers import MarkVideoSerializers
from rest_framework import status
from .serializers import YouTubeDetailSerializer

# Create your views here.

API_KEY = settings.YOUTUBE_KEY


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def keyword_search(request):
    URL = "https://www.googleapis.com/youtube/v3/search"
    q = request.GET.get("q")
    maxResults = 6
    params = {
        "part": "snippet",
        "q": q,
        "maxResults": maxResults,
        "key": API_KEY,
        "type": "video",
    }
    data = requests.get(url=URL, params=params)
    return Response(data.json())


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def mark_video(request):
    user = request.user
    videoId = request.data.get("videoId")
    channelTitle = request.data.get("channelTitle")
    title = request.data.get("title")
    thumbnailURL = request.data.get("thumbnailURL")

    marked = MarkedVideo.objects.filter(user=user, videoId=videoId).first()

    if marked:
        marked.delete()
        return Response(
            {"message": "삭제되었습니다."}, status=status.HTTP_204_NO_CONTENT
        )
    else:
        data = {
            "videoId": videoId,
            "channelTitle": channelTitle,
            "title": title,
            "thumbnailURL": thumbnailURL,
        }
        serializer = MarkVideoSerializers(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def marked_video(request):
    user = request.user.id
    video_list = MarkedVideo.objects.filter(user_id=user)
    serializers = MarkVideoSerializers(video_list, many=True)
    return Response(serializers.data)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def show_video(request, id):
    """
    GET /api/youtube/{id}/
    → YouTube Data API 에서 snippet.title, snippet.description 전체 가져오기
    """
    URL = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet",
        "id":   id,
        "key":  API_KEY,
    }
    resp = requests.get(URL, params=params)
    if resp.status_code != 200:
        return Response(
            {"detail": "YouTube API 호출 실패"},
            status=resp.status_code
        )

    items = resp.json().get("items", [])
    if not items:
        return Response(
            {"detail": "해당 영상이 없습니다."},
            status=status.HTTP_404_NOT_FOUND
        )

    snippet = items[0]["snippet"]
    data = {
        "id":          id,
        "title":       snippet.get("title", ""),
        "description": snippet.get("description", ""),
    }
    serializer = YouTubeDetailSerializer(data=data)
    serializer.is_valid(raise_exception=True)
    return Response(serializer.data)