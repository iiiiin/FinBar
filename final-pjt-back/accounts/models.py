from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
# from allauth.account.models import EmailAddress


class User(AbstractUser):
    age = models.PositiveIntegerField(null=False)
    nickname = models.CharField(max_length=150, null=False)


# suggests/models.py (또는 별도 앱에서 정의 가능)

User = get_user_model()


class InvestmentGoal(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="goal")
    current_asset = models.PositiveIntegerField(help_text="현재 자산 (만원)")
    target_asset = models.PositiveIntegerField(help_text="목표 자산 (만원)")
    target_years = models.PositiveIntegerField(help_text="목표까지 남은 기간 (년)")
    expected_annual_return = models.FloatField(
        null=True, blank=True, help_text="필요 예상 수익률 (%)")
    preferred_period = models.PositiveIntegerField(
        help_text="선호 투자 기간 (개월)", default=12)

    def calculate_required_return(self):
        try:
            r = ((self.target_asset / self.current_asset)
                 ** (1 / self.target_years)) - 1
            return round(r * 100, 2)  # 연평균 수익률 (%) 반환
        except ZeroDivisionError:
            return None


class InvestmentProfile(models.Model):
    RISK_TYPES = [
        ("안정형", "안정형"),
        ("안정추구형", "안정추구형"),
        ("위험중립형", "위험중립형"),
        ("적극투자형", "적극투자형"),
        ("공격투자형", "공격투자형"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    total_score = models.IntegerField()
    risk_type = models.CharField(max_length=20, choices=RISK_TYPES)
    evaluated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.risk_type}"
