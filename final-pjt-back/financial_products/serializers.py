# serializers.py
from .models import Stock
from rest_framework import serializers
from .models import (
    DepositProduct,
    DepositProductOptions,
    SavingProduct,
    SavingProductOptions,
)

# ────────────── 저장용 시리얼라이저 ──────────────


class DepositProductBulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        objs = [DepositProduct(**item) for item in validated_data]
        DepositProduct.objects.bulk_create(objs, ignore_conflicts=True)
        return objs


class DepositProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProduct
        fields = (
            "fin_co_no",
            "kor_co_nm",
            "fin_prdt_cd",
            "fin_prdt_nm",
            "join_way",
            "mtrt_int",
            "spcl_cnd",
            "join_deny",
            "join_member",
            "etc_note",
            "max_limit",
            "dcls_strt_day",
        )
        list_serializer_class = DepositProductBulkCreateListSerializer


class DepositProductOptionsBulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        objs = [DepositProductOptions(**item) for item in validated_data]
        DepositProductOptions.objects.bulk_create(objs, ignore_conflicts=True)
        return objs


class DepositProductOptionsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProductOptions
        fields = (
            "deposit_product_id",
            # "fin_prdt_cd",
            "intr_rate_type_nm",
            "save_trm",
            "intr_rate",
            "intr_rate2",
        )
        list_serializer_class = DepositProductOptionsBulkCreateListSerializer


class SavingProductBulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        objs = [SavingProduct(**item) for item in validated_data]
        SavingProduct.objects.bulk_create(objs, ignore_conflicts=True)
        return objs


class SavingProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingProduct
        fields = (
            "fin_co_no",
            "kor_co_nm",
            "fin_prdt_cd",
            "fin_prdt_nm",
            "join_way",
            "mtrt_int",
            "spcl_cnd",
            "join_deny",
            "join_member",
            "etc_note",
            "max_limit",
            "dcls_strt_day",
        )
        list_serializer_class = SavingProductBulkCreateListSerializer


class SavingProductOptionsBulkCreateListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        objs = [SavingProductOptions(**item) for item in validated_data]
        SavingProductOptions.objects.bulk_create(objs, ignore_conflicts=True)
        return objs


class SavingProductOptionsCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingProductOptions
        fields = (
            "saving_product_id",
            # "fin_prdt_cd",
            "intr_rate_type_nm",
            "rsrv_type_nm",
            "save_trm",
            "intr_rate",
            "intr_rate2",
        )
        list_serializer_class = SavingProductOptionsBulkCreateListSerializer


# ────────────── 출력용(Read-only) 시리얼라이저 ──────────────


class DepositProductOptionsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositProductOptions
        fields = (
            "deposit_product_id",
            "intr_rate_type_nm",
            "save_trm",
            "intr_rate",
            "intr_rate2",
        )


class DepositProductReadSerializer(serializers.ModelSerializer):
    options = DepositProductOptionsReadSerializer(
        source="depositproductoptions_set", many=True, read_only=True
    )

    class Meta:
        model = DepositProduct
        fields = (
            "fin_co_no",
            "kor_co_nm",
            "fin_prdt_cd",
            "fin_prdt_nm",
            "join_way",
            "mtrt_int",
            "spcl_cnd",
            "join_deny",
            "join_member",
            "etc_note",
            "max_limit",
            "dcls_strt_day",
            "options",
        )


class SavingProductOptionsReadSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingProductOptions
        fields = (
            "saving_product_id",
            "intr_rate_type_nm",
            "rsrv_type_nm",
            "save_trm",
            "intr_rate",
            "intr_rate2",
        )


class SavingProductReadSerializer(serializers.ModelSerializer):
    options = SavingProductOptionsReadSerializer(
        source="savingproductoptions_set", many=True, read_only=True
    )

    class Meta:
        model = SavingProduct
        fields = (
            "fin_co_no",
            "kor_co_nm",
            "fin_prdt_cd",
            "fin_prdt_nm",
            "join_way",
            "mtrt_int",
            "spcl_cnd",
            "join_deny",
            "join_member",
            "etc_note",
            "max_limit",
            "dcls_strt_day",
            "options",
        )

 # stocks/serializers.py


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = "__all__"
# ---------------추천 응답 시리얼라이저 --------------------------

# suggests/serializers.py


class DepositOptionSerializer(serializers.Serializer):
    save_trm = serializers.CharField()
    intr_rate2 = serializers.FloatField()


class SavingOptionSerializer(serializers.Serializer):
    save_trm = serializers.CharField()
    intr_rate2 = serializers.FloatField()


class DepositProductRecommendationSerializer(serializers.Serializer):
    type = serializers.CharField(default="예금")
    name = serializers.CharField(source="fin_prdt_nm")
    bank = serializers.CharField(source="kor_co_nm")
    product_code = serializers.CharField(source="fin_prdt_cd")
    category = serializers.CharField(default="예금")
    options = DepositOptionSerializer(many=True)


class SavingProductRecommendationSerializer(serializers.Serializer):
    type = serializers.CharField(default="적금")
    name = serializers.CharField(source="fin_prdt_nm")
    bank = serializers.CharField(source="kor_co_nm")
    product_code = serializers.CharField(source="fin_prdt_cd")
    category = serializers.CharField(default="적금")
    options = SavingOptionSerializer(many=True)


# 통합 응답 Serializer
class CombinedProductRecommendationSerializer(serializers.Serializer):
    recommendation_type = serializers.ChoiceField(choices=["예적금", "주식"])
    required_return = serializers.FloatField()
    items = serializers.ListField()


class StockRecommendationSerializer(serializers.Serializer):
    type = serializers.CharField(default="주식")
    name = serializers.CharField()
    code = serializers.CharField()
    market = serializers.CharField()
    sector = serializers.CharField()
    reason = serializers.CharField()


# suggests/serializers.py


class ProductOptionSerializer(serializers.Serializer):
    save_trm = serializers.CharField()
    intr_rate2 = serializers.FloatField()


class ProductRecommendationSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["예금", "적금"])
    name = serializers.CharField()
    bank = serializers.CharField()
    product_code = serializers.CharField()
    category = serializers.CharField()
    options = ProductOptionSerializer(many=True)


class DepositSavingRecommendationResponseSerializer(serializers.Serializer):
    recommendation_type = serializers.ChoiceField(choices=["예적금"])
    required_return = serializers.FloatField()
    items = ProductRecommendationSerializer(many=True)
