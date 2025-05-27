# views.py
import requests
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly

# 기본 위치: 서울시청
DEFAULT_LOCATION = {"lat": 37.5665, "lng": 126.9780}


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def resolve_map_location(request):
    """
    프론트에서 사용자 위치 정보를 전달 (lat, lng)
    → 없으면 기본 좌표(서울시청)로 응답
    """
    lat = request.data.get("lat")
    lng = request.data.get("lng")

    if lat and lng:
        try:
            lat = float(lat)
            lng = float(lng)
            return Response({"lat": lat, "lng": lng, "used_default": False})
        except ValueError:
            pass

    # 위치 정보 없음 → 기본 위치로
    return Response(
        {
            "lat": DEFAULT_LOCATION["lat"],
            "lng": DEFAULT_LOCATION["lng"],
            "used_default": True,
        }
    )


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def search_nearby_places(request):
    keyword = request.data.get("keyword")
    lat = request.data.get("lat")
    lng = request.data.get("lng")

    url = "https://dapi.kakao.com/v2/local/search/keyword.json"
    headers = {"Authorization": f"KakaoAK {settings.KAKAO_REST_API_KEY}"}
    params = {
        "query": keyword,
        "x": lng,  # 경도
        "y": lat,  # 위도
        "radius": 2000,  # 반경 2km 이내
        "sort": "distance",
    }

    resp = requests.get(url, headers=headers, params=params)
    data = resp.json()
    print(data)
    results = [
        {
            "place_name": doc["place_name"],
            "address_name": doc["address_name"],
            "x": doc["x"],  # 경도
            "y": doc["y"],  # 위도
        }
        for doc in data.get("documents", [])
    ]

    return Response(results)
