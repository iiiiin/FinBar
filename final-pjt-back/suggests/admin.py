from .models import ProductCategory, ProductRiskCategory
from django.contrib import admin
from .models import InvestmentQuestion, InvestmentChoice, StockRecommendation, Recommendation, RecommendationItem


class InvestmentChoiceInline(admin.TabularInline):
    model = InvestmentChoice
    extra = 1


@admin.register(InvestmentQuestion)
class InvestmentQuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "question_text")
    inlines = [InvestmentChoiceInline]


@admin.register(InvestmentChoice)
class InvestmentChoiceAdmin(admin.ModelAdmin):
    list_display = ["question", "choice_text", "score"]


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ("category_name",)


@admin.register(ProductRiskCategory)
class ProductRiskCategoryAdmin(admin.ModelAdmin):
    list_display = ("product_type", "category", "default_risk_level")


@admin.register(StockRecommendation)
class StockRecommendationAdmin(admin.ModelAdmin):
    list_display = ["user", "name", "code", "market", "sector", "recommended_at"]
    list_filter = ["market", "sector", "recommended_at"]
    search_fields = ["user__username", "name", "code"]
    readonly_fields = ["recommended_at"]


@admin.register(Recommendation)
class RecommendationAdmin(admin.ModelAdmin):
    list_display = ["user", "risk_type", "required_return", "created_at"]
    list_filter = ["risk_type", "created_at"]
    search_fields = ["user__username"]
    readonly_fields = ["created_at"]


@admin.register(RecommendationItem)
class RecommendationItemAdmin(admin.ModelAdmin):
    list_display = ["recommendation", "content_type", "object_id"]
    list_filter = ["content_type"]
