from django.urls import path
from . import views

app_name = 'investment_profile'

urlpatterns = [
    path('status/', views.check_profile_status, name='profile-status'),
    path('profile/', views.UserInvestmentProfileAPIView.as_view(), name='user-profile'),
    path('goal/', views.InvestmentGoalAPIView.as_view(), name='investment-goal'),
    path('goal/create/', views.create_investment_goal, name='create-investment-goal'),
    path('goal/progress/', views.get_investment_progress, name='investment-progress'),
    path('goal/update-asset/', views.update_current_asset, name='update-current-asset'),
    path('risk/', views.InvestmentProfileAPIView.as_view(), name='investment-profile'),
    path('risk/create/', views.create_investment_profile, name='create-investment-profile'),
] 