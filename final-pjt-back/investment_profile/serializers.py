from rest_framework import serializers
from .models import InvestmentGoal, InvestmentProfile
from my_products.serializers import (
    DepositBookmarkSerializer,
    SavingBookmarkSerializer,
    StockBookmarkSerializer,
)
from django.contrib.auth import get_user_model

class InvestmentGoalSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    remaining_amount = serializers.SerializerMethodField()
    days_remaining = serializers.SerializerMethodField()
    achievement_status = serializers.SerializerMethodField()
    
    class Meta:
        model = InvestmentGoal
        fields = (
            "current_asset",
            "target_asset",
            "target_years",
            "expected_annual_return",
            "preferred_period",
            "progress_percentage",
            "remaining_amount",
            "days_remaining",
            "achievement_status",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "expected_annual_return", 
            "progress_percentage", 
            "remaining_amount", 
            "days_remaining", 
            "achievement_status",
            "created_at",
            "updated_at",
        )

    def get_progress_percentage(self, obj):
        return obj.get_progress_percentage()
    
    def get_remaining_amount(self, obj):
        return obj.get_remaining_amount()
    
    def get_days_remaining(self, obj):
        return obj.get_days_remaining()
    
    def get_achievement_status(self, obj):
        return obj.get_achievement_status()

    def validate(self, data):
        # 생성 시에만 검증 (수정 시에는 일부 필드만 변경 가능)
        if self.instance is None:
            if not all(k in data for k in ['current_asset', 'target_asset', 'target_years']):
                raise serializers.ValidationError("현재 자산, 목표 자산, 목표 기간은 필수 입력 항목입니다.")
        
        if data.get("target_asset") and data.get("current_asset"):
            if data["target_asset"] <= data["current_asset"]:
                raise serializers.ValidationError("목표 자산은 현재 자산보다 커야 합니다.")
        
        if data.get("target_years") is not None and data["target_years"] <= 0:
            raise serializers.ValidationError("목표 기간은 1년 이상이어야 합니다.")
        
        return data

class InvestmentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestmentProfile
        fields = (
            "total_score",
            "risk_type",
            "evaluated_at",
        )
        read_only_fields = ("evaluated_at",)

class UserInvestmentProfileSerializer(serializers.ModelSerializer):
    investment_goal = InvestmentGoalSerializer(source='goal', read_only=True)
    investment_profile = InvestmentProfileSerializer(read_only=True)
    deposit_bookmarks = DepositBookmarkSerializer(many=True, read_only=True)
    saving_bookmarks = SavingBookmarkSerializer(many=True, read_only=True)
    stock_bookmarks = StockBookmarkSerializer(many=True, read_only=True)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "username",
            "email",
            "age",
            "nickname",
            "investment_goal",
            "investment_profile",
            "deposit_bookmarks",
            "saving_bookmarks",
            "stock_bookmarks",
        )
        read_only_fields = ("username", "email") 