
from .models import DepositProduct
from .models import SavingProduct
from django.shortcuts import render

from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import DepositProduct, SavingProduct
from .serializers import (
    DepositProductReadSerializer,
    SavingProductReadSerializer,
)
from .pagination import CustomPageNumberPagination


class DepositProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /products/deposits/        → 예금 상품 리스트
    GET  /products/deposits/{pk}/   → 단건 조회
    """
    queryset = DepositProduct.objects.prefetch_related(
        "depositproductoptions").order_by('-dcls_strt_day')
    serializer_class = DepositProductReadSerializer
    pagination_class = CustomPageNumberPagination


class SavingProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /products/savings/         → 적금 상품 리스트
    GET  /products/savings/{pk}/    → 단건 조회
    """
    queryset = SavingProduct.objects.prefetch_related(
        "savingproductoptions").order_by('-dcls_strt_day')
    serializer_class = SavingProductReadSerializer
    pagination_class = CustomPageNumberPagination
