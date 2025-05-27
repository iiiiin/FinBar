# views.py
from rest_framework.viewsets import ReadOnlyModelViewSet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

from .models import DepositProduct, SavingProduct
from .serializers import (
    DepositProductReadSerializer,
    SavingProductReadSerializer,
    DepositProductOptionReadSerializer,
    SavingProductOptionReadSerializer,
)
from .pagination import CustomPageNumberPagination
from .models import DepositProductOptions, SavingProductOptions


class DepositProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /products/deposits/        → 예금 상품 리스트
    GET  /products/deposits/{pk}/   → 단건 조회
    """

    queryset = DepositProduct.objects.prefetch_related("depositproductoptions")
    serializer_class = DepositProductReadSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        # 은행명으로 필터링
        "kor_co_nm": ["exact"],
        # 옵션의 만기(개월)로 필터링
        "depositproductoptions__save_trm": ["exact"],
    }
    # 정렬 가능한 필드
    ordering_fields = [
        "dcls_strt_day",  # 기본 공개일
        "kor_co_nm",  # 은행명 순
        "depositproductoptions__intr_rate",  # 이율
        "depositproductoptions__intr_rate2",  # 복리이율
    ]
    # 기본 정렬
    ordering = ["-dcls_strt_day"]


class SavingProductViewSet(ReadOnlyModelViewSet):
    """
    GET  /products/savings/         → 적금 상품 리스트
    GET  /products/savings/{pk}/    → 단건 조회
    """

    queryset = SavingProduct.objects.prefetch_related("savingproductoptions")
    serializer_class = SavingProductReadSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "kor_co_nm": ["exact"],
        "savingproductoptions__save_trm": ["exact"],
    }
    ordering_fields = [
        "dcls_strt_day",
        "kor_co_nm",
        "savingproductoptions__intr_rate",
        "savingproductoptions__intr_rate2",
    ]
    ordering = ["-dcls_strt_day"]


class DepositOptionViewSet(ReadOnlyModelViewSet):
    """
    GET /api/products/deposit-options/
    → 상품-옵션 쌍 리스트 (페이징·필터·정렬)
    """

    queryset = DepositProductOptions.objects.select_related("deposit_product")
    serializer_class = DepositProductOptionReadSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "deposit_product__kor_co_nm": ["exact"],  # 은행 필터
        "save_trm": ["exact"],  # 만기 필터
    }
    ordering_fields = ["save_trm", "intr_rate", "intr_rate2"]
    ordering = ["save_trm"]


class SavingOptionViewSet(ReadOnlyModelViewSet):
    """
    GET /api/products/deposit-options/
    → 상품-옵션 쌍 리스트 (페이징·필터·정렬)
    """

    queryset = SavingProductOptions.objects.select_related("saving_product")
    serializer_class = SavingProductOptionReadSerializer
    pagination_class = CustomPageNumberPagination

    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = {
        "saving_product__kor_co_nm": ["exact"],  # 은행 필터
        "save_trm": ["exact"],  # 만기 필터
    }
    ordering_fields = ["save_trm", "intr_rate", "intr_rate2"]
    ordering = ["save_trm"]
