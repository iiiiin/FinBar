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


class ProductCategory(models.Model):
    """
    상품을 대분류합니다. 예: 예금, 적금, 금, 은, 주식 등
    """
    CATEGORY_CHOICES = [
        ("예금", "예금"),
        ("적금", "적금"),
        ("금", "금"),
        ("은", "은"),
        ("주식", "주식"),
    ]

    category_name = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES, unique=True)

    def __str__(self):
        return self.category_name


class ProductRiskCategory(models.Model):
    """
    상품 세부 유형별 위험도와 분류(카테고리)를 저장합니다.
    예: '금ETF' → '금' 카테고리, 위험도 'medium'
    """
    product_type = models.CharField(max_length=30, unique=True)
    default_risk_level = models.CharField(max_length=10, choices=[
        ("low", "낮음"),
        ("medium", "중간"),
        ("high", "높음"),
    ])
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_type} ({self.category}) → {self.default_risk_level}"

# suggests/models.py


User = get_user_model()


class StockRecommendation(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="stock_recommendations")
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=20)
    market = models.CharField(max_length=20)
    sector = models.CharField(max_length=50)
    reason = models.TextField()
    recommended_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-recommended_at"]
