from django.urls import path
from . import views

urlpatterns = [
    # 기본 목록 조회
    path("", views.keyword_search),
    # 저장용
    path("mark/", views.mark_video),
    # 저장한 영상 리스트 확인용
    path("marked/", views.marked_video),
    # 단일 영상 확인용
    path("show_video/", views.show_video),
    # 4) 동영상 디테일 → GET  /api/youtube/{videoId}/
    path("<str:id>/", views.show_video),
]
