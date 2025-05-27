from django.db import models
from django.conf import settings
from financial_products.models import Stock
# Create your models here.


class MockInvestment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="기본 포트폴리오")
    virtual_cash = models.PositiveIntegerField(default=1000)  # 만원 단위
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"


class MockInvestmentTransaction(models.Model):
    investment = models.ForeignKey(
        MockInvestment, on_delete=models.CASCADE, related_name="transactions")
    stock = models.ForeignKey(Stock, on_delete=models.SET_NULL, null=True)
    is_buy = models.BooleanField()  # True=매수, False=매도
    quantity = models.PositiveIntegerField()
    price_per_unit = models.FloatField()
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{'매수' if self.is_buy else '매도'} {self.stock.stock_name} x {self.quantity}"
