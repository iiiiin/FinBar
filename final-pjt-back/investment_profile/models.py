from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from django.utils import timezone

class InvestmentGoal(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investment_goal")
    current_asset = models.PositiveIntegerField(
        help_text="현재 자산 (만원)",
        validators=[
            MinValueValidator(1, message="현재 자산은 1만원 이상이어야 합니다."),
            MaxValueValidator(1000000, message="현재 자산은 10억원(100만 만원) 이하여야 합니다.")
        ]
    )
    target_asset = models.PositiveIntegerField(
        help_text="목표 자산 (만원)",
        validators=[
            MinValueValidator(1, message="목표 자산은 1만원 이상이어야 합니다."),
            MaxValueValidator(10000000, message="목표 자산은 100억원(1000만 만원) 이하여야 합니다.")
        ]
    )
    target_years = models.PositiveIntegerField(
        help_text="목표까지 남은 기간 (년)",
        validators=[
            MinValueValidator(1, message="목표 기간은 1년 이상이어야 합니다."),
            MaxValueValidator(50, message="목표 기간은 50년 이하여야 합니다.")
        ]
    )
    expected_annual_return = models.FloatField(
        null=True, blank=True, 
        help_text="필요 예상 수익률 (%)",
        validators=[
            MinValueValidator(-50, message="예상 수익률은 -50% 이상이어야 합니다."),
            MaxValueValidator(100, message="예상 수익률은 100% 이하여야 합니다.")
        ]
    )
    preferred_period = models.PositiveIntegerField(
        help_text="선호 투자 기간 (개월)", 
        default=12,
        validators=[
            MinValueValidator(1, message="선호 투자 기간은 1개월 이상이어야 합니다."),
            MaxValueValidator(360, message="선호 투자 기간은 360개월(30년) 이하여야 합니다.")
        ]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        super().clean()
        # 목표 자산이 현재 자산보다 작거나 같은 경우 검증
        if self.target_asset and self.current_asset:
            if self.target_asset <= self.current_asset:
                raise ValidationError({
                    'target_asset': '목표 자산은 현재 자산보다 커야 합니다.'
                })
        
        # 필요 수익률이 비현실적으로 높은 경우 경고
        if self.expected_annual_return and self.expected_annual_return > 50:
            raise ValidationError({
                'expected_annual_return': '연간 50% 이상의 수익률은 매우 높은 위험을 동반합니다.'
            })

    def calculate_required_return(self):
        try:
            if self.current_asset <= 0 or self.target_years <= 0:
                return None
            r = ((self.target_asset / self.current_asset)
                 ** (1 / self.target_years)) - 1
            return round(r * 100, 2)  # 연평균 수익률 (%) 반환
        except (ZeroDivisionError, ValueError):
            return None

    def save(self, *args, **kwargs):
        if not self.preferred_period:
            self.preferred_period = 12  # 기본값 설정
        self.full_clean()
        super().save(*args, **kwargs)

    def get_progress_percentage(self):
        """목표 달성률을 계산합니다 (%)"""
        if not self.target_asset or not self.current_asset:
            return 0
        
        if self.target_asset <= self.current_asset:
            return 100.0
        
        progress = ((self.current_asset) / self.target_asset) * 100
        return round(progress, 2)

    def get_remaining_amount(self):
        """목표까지 남은 금액을 계산합니다 (만원)"""
        if not self.target_asset or not self.current_asset:
            return 0
        
        remaining = self.target_asset - self.current_asset
        return max(0, remaining)

    def get_days_remaining(self):
        """목표까지 남은 일수를 계산합니다"""
        if not self.target_years:
            return 0
        
        # 생성일로부터 목표 기간 계산
        target_date = self.created_at + timedelta(days=self.target_years * 365)
        now = timezone.now()  # timezone-aware 현재 시간 사용
        remaining = (target_date - now).days
        
        return max(0, remaining)

    def get_achievement_status(self):
        """목표 달성 상태를 반환합니다"""
        progress = self.get_progress_percentage()
        
        if progress >= 100:
            return "달성완료"
        elif progress >= 75:
            return "달성임박"
        elif progress >= 50:
            return "순조로운진행"
        elif progress >= 25:
            return "초기단계"
        else:
            return "시작단계"

    def __str__(self):
        return f"{self.user.username}의 투자 목표 - 달성률: {self.get_progress_percentage()}%"


class InvestmentProfile(models.Model):
    RISK_TYPES = [
        ("안정형", "안정형"),
        ("안정추구형", "안정추구형"),
        ("위험중립형", "위험중립형"),
        ("적극투자형", "적극투자형"),
        ("공격투자형", "공격투자형"),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="investment_profile")
    total_score = models.IntegerField()
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.risk_type}"
