from datetime import datetime

from .models import Stock, DepositProduct
from .models import SavingProduct
from django.shortcuts import render
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.decorators import api_view
from rest_framework.authentication import TokenAuthentication
from rest_framework.viewsets import ReadOnlyModelViewSet

from rest_framework.decorators import action
from .services import fetch_and_upsert_saving
from .services import fetch_and_upsert_deposit
from django_celery_beat.models import PeriodicTask

# views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import DepositProduct, SavingProduct
from .serializers import (
    DepositProductReadSerializer,
    SavingProductReadSerializer,
)

class DepositProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /api/deposits/        → 예금 상품 리스트
    GET  /api/deposits/{pk}/   → 단건 조회
    """
    queryset = DepositProduct.objects.all().order_by('-dcls_strt_day')
    serializer_class = DepositProductReadSerializer

class SavingProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /api/savings/         → 적금 상품 리스트
    GET  /api/savings/{pk}/    → 단건 조회
    """
    queryset = SavingProduct.objects.all().order_by('-dcls_strt_day')
    serializer_class = SavingProductReadSerializer
