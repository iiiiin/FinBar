from rest_framework.decorators import api_view
from financial_products.models import DepositProduct, SavingProduct, FinancialCompanyDeposit, FinancialCompanySaving
from rest_framework.response import Response
from .models import DepositProduct
from rest_framework.viewsets import ReadOnlyModelViewSet
from .models import DepositProduct, SavingProduct
from .serializers import (
    DepositProductReadSerializer,
    SavingProductReadSerializer,
)
from .pagination import CustomPageNumberPagination


class DepositProductViewSet(ReadOnlyModelViewSet):
    """
    GET /api/products/deposits/?page=1
    GET /api/products/deposits/?company_id=2
    """
    queryset = DepositProduct.objects.select_related('financial_company', 'category')\
                                     .order_by('-dcls_strt_day')
    serializer_class = DepositProductReadSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")
        if company_id:
            queryset = queryset.filter(financial_company_id=company_id)
        return queryset


class SavingProductViewSet(ReadOnlyModelViewSet):
    """
    GET /api/products/savings/?page=1
    GET /api/products/savings/?company_id=3
    """
    queryset = SavingProduct.objects.select_related('financial_company', 'category')\
                                    .order_by('-dcls_strt_day')
    serializer_class = SavingProductReadSerializer
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        queryset = super().get_queryset()
        company_id = self.request.query_params.get("company_id")
        if company_id:
            queryset = queryset.filter(financial_company_id=company_id)
        return queryset


@api_view(["GET"])
def deposit_companies(request):
    """
    예금 상품에 해당하는 금융회사 목록 반환
    """
    company_ids = DepositProduct.objects.values_list(
        "financial_company_id", flat=True).distinct()
    companies = FinancialCompanyDeposit.objects.filter(
        id__in=company_ids).order_by("kor_co_nm")
    data = [{"id": c.id, "name": c.kor_co_nm} for c in companies]
    return Response(data)


@api_view(["GET"])
def saving_companies(request):
    """
    적금 상품에 해당하는 금융회사 목록 반환
    """
    company_ids = SavingProduct.objects.values_list(
        "financial_company_id", flat=True).distinct()
    companies = FinancialCompanySaving.objects.filter(
        id__in=company_ids).order_by("kor_co_nm")
    data = [{"id": c.id, "name": c.kor_co_nm} for c in companies]
    return Response(data)
