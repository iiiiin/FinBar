# suggests/views.py
from accounts.models import InvestmentGoal, InvestmentProfile
from financial_products.serializers import (
    ProductRecommendationSerializer,
    DepositSavingRecommendationResponseSerializer,
)
from suggests.services.strategy import determine_recommendation_factors
from .services.openai_client import build_stock_prompt, ask_gpt_for_product_recommendation
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from accounts.serializers import InvestmentGoalSerializer
from .models import InvestmentQuestion, InvestmentChoice
from .serializers import (
    InvestmentQuestionSerializer,
    InvestmentAnswerSerializer,
    StockRecommendationCreateSerializer
)
from suggests.services.recommendation import _get_top_product_recommendations
from suggests.services.recommendation import (
    get_deposit_only_recommendations,
    get_saving_only_recommendations,
    get_deposit_saving_recommendations,
)

RISK_LEVEL = {
    "안정형": ["low"],
    "안정추구형": ["low", "medium"],
    "위험중립형": ["medium"],
    "적관통자형": ["medium", "high"],
    "공격통자형": ["high"],
}

MARKET_CHOICES = ["KOSPI", "KOSDAQ", "KONEX"]
SECTOR_CHOICES = [
    "반동체", "바이오", "2차전지", "자동차",
    "금융", "건설", "에너지", "유통", "플랫폼", "기타"
]


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_investment_questions(request):
    questions = InvestmentQuestion.objects.all()
    serializer = InvestmentQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_investment_answers(request):
    serializer = InvestmentAnswerSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        answers = serializer.validated_data["answers"]
        total_score = 0
        for ans in answers:
            try:
                choice = InvestmentChoice.objects.get(id=ans["choice_id"])
                total_score += choice.score
            except InvestmentChoice.DoesNotExist:
                return Response({"error": "Invalid choice ID"}, status=400)

        if total_score <= 7:
            risk_type = "안정형"
        elif total_score <= 11:
            risk_type = "안정추구형"
        elif total_score <= 15:
            risk_type = "위험중립형"
        elif total_score <= 19:
            risk_type = "적관통자형"
        else:
            risk_type = "공격통자형"

        profile, _ = InvestmentProfile.objects.update_or_create(
            user=request.user,
            defaults={"total_score": total_score, "risk_type": risk_type},
        )

        return Response({
            "risk_type": profile.risk_type,
            "total_score": profile.total_score,
            "evaluated_at": profile.evaluated_at,
        })

# suggests/views.py


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_recommended_stocks(request):
    serializer = StockRecommendationCreateSerializer(
        data=request.data, many=True, context={"request": request})
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "추천 종목 저장 완료"}, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def investment_goal_view(request):
    user = request.user

    try:
        goal = user.goal
    except InvestmentGoal.DoesNotExist:
        if request.method == "GET":
            return Response({"detail": "목표 자사 정보가 없습니다."}, status=404)
        goal = None

    if request.method == "GET":
        serializer = InvestmentGoalSerializer(goal)
        return Response(serializer.data)

    serializer = InvestmentGoalSerializer(
        instance=goal, data=request.data, partial=True)
    if serializer.is_valid():
        goal = serializer.save(user=user)
        goal.expected_annual_return = goal.calculate_required_return()
        goal.save()
        return Response(InvestmentGoalSerializer(goal).data)
    return Response(serializer.errors, status=400)


def parse_required_return_param(request):
    """공통된 required_return 파라미터 처리"""
    required_return = request.GET.get("required_return")
    if not required_return:
        return None, Response({"error": "required_return 필드가 필요합니다."}, status=400)
    try:
        return float(required_return), None
    except ValueError:
        return None, Response({"error": "올바른 수익률을 입력해주세요."}, status=400)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def investment_product_recommendation_view(request):
    user = request.user

    try:
        profile = user.investmentprofile
        goal = user.goal
    except (InvestmentProfile.DoesNotExist, InvestmentGoal.DoesNotExist):
        return Response({"detail": "투자 성향 또는 목표 자산 정보가 없습니다."}, status=400)

    required_return = goal.calculate_required_return()
    goal.expected_annual_return = required_return
    goal.save()

    selected_market = request.GET.get("market")
    selected_sector = request.GET.get("sector")
    category = request.GET.get("category")  # optional

    user_info = {
        "risk_type": profile.risk_type,
        "required_return": required_return,
    }

    from suggests.services.strategy import determine_recommendation_factors
    factors = determine_recommendation_factors(
        required_return, profile.risk_type, goal.preferred_period
    )
    recommendation_type = factors["final"]

    if recommendation_type == "예금":
        return include_factors(_handle_deposit(required_return), factors)

    elif recommendation_type == "예적금 혼합":
        return include_factors(_handle_deposit_saving(required_return, category), factors)

    elif recommendation_type in ["적금 + 주식(안정형)", "적금+주식"]:
        return include_factors(
            _handle_saving_plus_stock(
                required_return, user_info, selected_market, selected_sector),
            factors
        )

    elif recommendation_type.startswith("주식"):
        return include_factors(
            _handle_stock_only(required_return, user_info,
                               selected_market, selected_sector),
            factors
        )

    elif recommendation_type.startswith("경고"):
        return include_factors(
            _handle_warning(required_return, category),
            factors
        )

    return Response({"detail": "추천 조건이 일치하지 않습니다."}, status=400)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deposit_only_recommendation_view(request):
    required_return, error = parse_required_return_param(request)
    if error:
        return error

    return _handle_deposit(required_return)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def saving_only_recommendation_view(request):
    required_return, error = parse_required_return_param(request)
    if error:
        return error

    return _handle_saving(required_return)


# 🔽 핸들러 함수 분리

def _handle_deposit(required_return):
    items = get_deposit_only_recommendations(required_return)

    if not items:
        return Response({
            "recommendation_type": "예금",
            "required_return": required_return,
            "message": "조건을 만족하는 예금 상품이 없습니다.",
            "items": []
        })

    serializer = ProductRecommendationSerializer(items, many=True)
    return Response({
        "recommendation_type": "예금",
        "required_return": required_return,
        "items": serializer.data
    })


def _handle_saving(required_return):
    items = get_saving_only_recommendations(required_return)

    if not items:
        return Response({
            "recommendation_type": "적금",
            "required_return": required_return,
            "message": "조건을 만족하는 적금 상품이 없습니다.",
            "items": []
        })

    serializer = ProductRecommendationSerializer(items, many=True)
    return Response({
        "recommendation_type": "적금",
        "required_return": required_return,
        "items": serializer.data
    })


def _handle_deposit_saving(required_return, category=None):
    items = get_deposit_saving_recommendations(required_return, category)

    if not items:
        return Response({
            "recommendation_type": "예적금",
            "required_return": required_return,
            "message": "조건을 만족하는 예금/적금 상품이 없습니다.",
            "items": []
        })

    serializer = DepositSavingRecommendationResponseSerializer({
        "recommendation_type": "예적금",
        "required_return": required_return,
        "items": items
    })
    return Response(serializer.data)


def _handle_saving_plus_stock(required_return, user_info, market, sector):
    saving_items = get_saving_only_recommendations(required_return)
    saving_serializer = ProductRecommendationSerializer(
        saving_items, many=True)

    prompt = build_stock_prompt(user_info, market, sector)
    stock_items = ask_gpt_for_product_recommendation(prompt)

    return Response({
        "recommendation_type": "적금+주식",
        "required_return": required_return,
        "items": saving_serializer.data + stock_items
    })


def _handle_stock_only(required_return, user_info, market, sector):
    prompt = build_stock_prompt(user_info, market, sector)
    stock_items = ask_gpt_for_product_recommendation(prompt)

    return Response({
        "recommendation_type": "주식",
        "required_return": required_return,
        "items": stock_items
    })


def _handle_warning(required_return, category=None):
    items = get_deposit_saving_recommendations(required_return, category)
    serializer = DepositSavingRecommendationResponseSerializer({
        "recommendation_type": "예적금",
        "required_return": required_return,
        "warning": "현재 투자 성향과 기간으로는 목표 수익률 달성이 어렵습니다. 수익률을 조정하거나 투자 기간을 늘리는 것을 고려해 보세요.",
        "items": items
    })
    return Response(serializer.data)


def include_factors(response, factors):
    if isinstance(response, Response):
        response.data["factors"] = factors
    return response
