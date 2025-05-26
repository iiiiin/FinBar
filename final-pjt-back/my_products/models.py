# models.py
from django.conf import settings
from django.db import models
from financial_products.models import DepositProduct, SavingProduct, Stock


class StockBookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="stock_bookmarks",
    )
    stock_product = models.ForeignKey(
        Stock, on_delete=models.CASCADE, related_name="bookmarked_stock"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stock_product")
        ordering = ["-created_at"]


class DepositBookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="deposit_bookmarks",
    )
    deposit_product = models.ForeignKey(
        DepositProduct, on_delete=models.CASCADE, related_name="bookmarked_deposits"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "deposit_product")
        ordering = ["-created_at"]


class SavingBookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="saving_bookmarks",
    )
    saving_product = models.ForeignKey(
        SavingProduct, on_delete=models.CASCADE, related_name="bookmarked_savings"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "saving_product")
        ordering = ["-created_at"]
