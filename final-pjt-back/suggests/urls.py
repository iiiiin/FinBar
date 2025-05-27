from django.urls import path
from . import views

urlpatterns = [
    # 투자 성향 진단
    path("questions/", views.get_investment_questions),
    path("submit/", views.submit_investment_answers),
    # 자산 목표 등록 및 조회
    path("set-goal/", views.investment_goal_view, name="investment-goal"),
    # 고급 추천 (수익률 + 성향 + 기간 기반 자동 분기)
    path(
        "by-goal/",
        views.investment_product_recommendation_view,
        name="recommendation-by-goal",
    ),
    # 수익률 기반 단독 예적금 추천 (테스트용 또는 선택형)
    path(
        "deposit-only/",
        views.deposit_only_recommendation_view,
        name="deposit-only-recommendation",
    ),
    path(
        "saving-only/",
        views.saving_only_recommendation_view,
        name="saving-only-recommendation",
    ),
    # 주식 추천 저장
    path("save-stocks/", views.save_recommended_stocks, name="save-recommended-stocks"),
    # 저장된 추천 상품 조회
    path(
        "saved-recommendations/",
        views.get_saved_recommendations,
        name="get-saved-recommendations",
    ),
    path(
        "saved-recommendations/<int:pk>/",
        views.delete_saved_recommendation,
        name="delete_saved_recommendation",
    ),
    path(
        "saved-recommendations/delete-all/",
        views.delete_all_saved_recommendations,
        name="delete_all_saved_recommendations",
    ),
]
