from rest_framework import serializers
from .models import DepositBookmark, SavingBookmark, StockBookmark
from financial_products.models import DepositProduct, SavingProduct, Stock

# serializers.py
from rest_framework import serializers
from .models import DepositBookmark, SavingBookmark
from financial_products.serializers import (
    DepositProductReadSerializer,
    SavingProductReadSerializer,
)


class DepositBookmarkSerializer(serializers.ModelSerializer):
    # 1) 상세 정보용 중첩 시리얼라이저
    deposit_product = DepositProductReadSerializer(read_only=True)
    # 2) 생성 시에는 PK로만 받도록 분리
    deposit_product_id = serializers.PrimaryKeyRelatedField(
        source="deposit_product", queryset=DepositProduct.objects.all(), write_only=True
    )

    class Meta:
        model = DepositBookmark
        fields = [
            "id",
            "deposit_product",  # read → nested detail
            "deposit_product_id",  # write → PK
            "created_at",
        ]
        read_only_fields = ["id", "deposit_product", "created_at"]


class SavingBookmarkSerializer(serializers.ModelSerializer):
    saving_product = SavingProductReadSerializer(read_only=True)
    saving_product_id = serializers.PrimaryKeyRelatedField(
        source="saving_product", queryset=SavingProduct.objects.all(), write_only=True
    )

    class Meta:
        model = SavingBookmark
        fields = [
            "id",
            "saving_product",
            "saving_product_id",
            "created_at",
        ]
        read_only_fields = ["id", "saving_product", "created_at"]


class StockReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = [
            "stock_code",
            "stock_name",
            "stock_name_en",
            "first_trade_date",
            "market",
            "security_type",
            "market_division",
            "stock_type",
            "face_value",
            "listed_shares",
            "risk_level",
            "category",
        ]


class StockBookmarkSerializer(serializers.ModelSerializer):
    # 조회 시 중첩 출력
    stock_product = StockReadSerializer(read_only=True)
    # 생성 시에는 ID로만 받음
    stock_product_id = serializers.PrimaryKeyRelatedField(
        source="stock_product", queryset=Stock.objects.all(), write_only=True
    )

    class Meta:
        model = StockBookmark
        fields = [
            "id",
            "stock_product",  # 중첩된 상세 정보
            "stock_product_id",  # POST 시 사용
            "created_at",
        ]
        read_only_fields = ["id", "stock_product", "created_at"]
