from django.contrib import admin
from .models import InvestmentProfile
# Register your models here.


@admin.register(InvestmentProfile)
class InvestmentProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "risk_type", "total_score", "evaluated_at")
