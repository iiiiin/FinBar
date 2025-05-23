from rest_framework.mixins import CreateModelMixin
from rest_framework.viewsets import GenericViewSet
from rest_framework import serializers
from .models import PriceData

# 1. Bulk 처리를 담당할 ListSerializer


class BulkPriceDataListSerializer(serializers.ListSerializer):
    def create(self, validated_data):
        # PriceData 인스턴스 리스트 생성
        objs = [PriceData(**item) for item in validated_data]
        # 중복은 무시하고 bulk insert
        PriceData.objects.bulk_create(objs, ignore_conflicts=True)
        return objs

# 2. 각 항목을 검증할 ItemSerializer


class PriceDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = PriceData
        fields = ('symbol', 'timestamp', 'price')
        # many=True 시 BulkPriceDataListSerializer 사용
        list_serializer_class = BulkPriceDataListSerializer


# 3. 뷰(ViewSet 등)에서 사용 예시


class PriceDataViewSet(CreateModelMixin, GenericViewSet):
    queryset = PriceData.objects.all()
    serializer_class = PriceDataSerializer

    # POST로 [{...}, {...}, ...] 형태의 리스트를 받으면 bulk로 처리됩니다.
