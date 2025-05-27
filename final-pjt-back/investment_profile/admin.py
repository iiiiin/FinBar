from django.contrib import admin
from .models import InvestmentGoal, InvestmentProfile


@admin.register(InvestmentGoal)
class InvestmentGoalAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'current_asset', 
        'target_asset', 
        'target_years', 
        'expected_annual_return',
        'get_progress_percentage',
        'get_achievement_status',
        'created_at'
    ]
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['expected_annual_return', 'created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage()}%"
    get_progress_percentage.short_description = '달성률'
    
    def get_achievement_status(self, obj):
        return obj.get_achievement_status()
    get_achievement_status.short_description = '달성 상태'


@admin.register(InvestmentProfile)  
class InvestmentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'risk_type', 'total_score', 'evaluated_at']
    list_filter = ['risk_type', 'evaluated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['evaluated_at']
