from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class InvestmentQuestion(models.Model):
    question_text = models.CharField(max_length=255)

    def __str__(self):
        return self.question_text


class InvestmentChoice(models.Model):
    question = models.ForeignKey(
        InvestmentQuestion, related_name="choices", on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=255)
    score = models.IntegerField(help_text="선택 시 가산될 점수")

    def __str__(self):
        return f"{self.question} - {self.choice_text}"


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
