from .models import ProductCategory, ProductRiskCategory
from django.contrib import admin
from .models import InvestmentQuestion, InvestmentChoice


class InvestmentChoiceInline(admin.TabularInline):
    model = InvestmentChoice
    extra = 1


@admin.register(InvestmentQuestion)
class InvestmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text")
    inlines = [InvestmentChoiceInline]


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name",)


@admin.register(ProductRiskCategory)
class ProductRiskCategoryAdmin(admin.ModelAdmin):
    list_display = ("product_type", "category", "default_risk_level")
