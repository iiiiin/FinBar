# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from .models import DepositBookmark, SavingBookmark, StockBookmark
from .serializers import (
    DepositBookmarkSerializer,
    SavingBookmarkSerializer,
    StockBookmarkSerializer,
)


class DepositBookmarkViewSet(viewsets.ModelViewSet):
    """
    GET    bookmarks/deposits/       → 내 예금 북마크 목록 조회
    POST   bookmarks/deposits/       → 예금 북마크 추가
    DELETE bookmarks/deposits/{pk}/  → 예금 북마크 삭제
    """

    serializer_class = DepositBookmarkSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DepositBookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavingBookmarkViewSet(viewsets.ModelViewSet):
    """
    GET    bookmarks/savings/        → 내 적금 북마크 목록 조회
    POST   bookmarks/savings/        → 적금 북마크 추가
    DELETE bookmarks/savings/{pk}/   → 적금 북마크 삭제
    """

    serializer_class = SavingBookmarkSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavingBookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class StockBookmarkViewSet(viewsets.ModelViewSet):
    """
    GET    bookmarks/stocks/        → 내 주식 북마크 목록 조회
    POST   bookmarks/stocks/        → 주식 북마크 추가
    DELETE bookmarks/stocks/{pk}/   → 주식 북마크 삭제
    """

    serializer_class = StockBookmarkSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return StockBookmark.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
