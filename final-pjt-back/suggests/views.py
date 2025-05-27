# suggests/views.py
from investment_profile.models import InvestmentGoal, InvestmentProfile
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

from investment_profile.serializers import InvestmentGoalSerializer
from .models import InvestmentQuestion, InvestmentChoice, Recommendation
from .serializers import (
    InvestmentQuestionSerializer,
    InvestmentAnswerSerializer,
    StockRecommendationCreateSerializer
)
from suggests.services.temp import _get_top_product_recommendations
from suggests.services.temp import (
    get_deposit_only_recommendations,
    get_saving_only_recommendations,
    get_deposit_saving_recommendations,
)

RISK_LEVEL = {
    "안정형": ["low"],
    "안정추구형": ["low", "medium"],
    "위험중립형": ["medium"],
    "적극투자형": ["medium", "high"],
    "공격투자형": ["high"],
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
    try:
        serializer = InvestmentAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({"error": "Invalid data format", "details": serializer.errors}, status=400)

        answers = serializer.validated_data["answers"]
        if not answers:
            return Response({"error": "No answers provided"}, status=400)

        total_score = 0
        for ans in answers:
            try:
                question_id = ans.get("question_id")
                choice_id = ans.get("choice_id")

                if not question_id or not choice_id:
                    return Response({"error": f"Invalid answer format: {ans}"}, status=400)

                # 질문 존재 여부 확인
                if not InvestmentQuestion.objects.filter(id=question_id).exists():
                    return Response({"error": f"Question {question_id} does not exist"}, status=400)

                choice = InvestmentChoice.objects.get(
                    id=choice_id, question_id=question_id)
                total_score += choice.score
            except InvestmentChoice.DoesNotExist:
                return Response(
                    {"error": f"Invalid choice ID {choice_id} for question {question_id}"},
                    status=400
                )
            except Exception as e:
                return Response({"error": str(e)}, status=400)

        # 점수에 따른 위험 유형 결정
        if total_score <= 7:
            risk_type = "안정형"
        elif total_score <= 11:
            risk_type = "안정추구형"
        elif total_score <= 15:
            risk_type = "위험중립형"
        elif total_score <= 19:
            risk_type = "적극투자형"
        else:
            risk_type = "공격투자형"

        # 프로필 업데이트 또는 생성
        try:
            profile, _ = InvestmentProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    "total_score": total_score,
                    "risk_type": risk_type
                }
            )

            return Response({
                "risk_type": profile.risk_type,
                "total_score": profile.total_score,
                "evaluated_at": profile.evaluated_at
            })
        except Exception as e:
            return Response({"error": f"Failed to update profile: {str(e)}"}, status=500)

    except Exception as e:
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


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
    """
    [DEPRECATED] 이 API는 더 이상 사용되지 않습니다.
    대신 /api/investment-profile/goal/ 엔드포인트를 사용하세요.

    - GET: /api/investment-profile/goal/
    - POST: /api/investment-profile/goal/create/
    - PATCH: /api/investment-profile/goal/
    """
    return Response({
        "message": "이 API는 deprecated 되었습니다.",
        "new_endpoints": {
            "get": "/api/investment-profile/goal/",
            "create": "/api/investment-profile/goal/create/",
            "update": "/api/investment-profile/goal/"
        }
    }, status=status.HTTP_410_GONE)


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
        profile = user.investment_profile
        goal = user.investment_goal
    except (InvestmentProfile.DoesNotExist, InvestmentGoal.DoesNotExist):
        return Response({"detail": "투자 성향 또는 목표 자산 정보가 없습니다."}, status=400)

    required_return = goal.calculate_required_return()
    preferred_period = goal.preferred_period
    goal.expected_annual_return = required_return
    goal.save()

    selected_market = request.GET.get("market")
    selected_sector = request.GET.get("sector")
    category = request.GET.get("category")  # optional

    # preferred_period는 쿼리 파라미터가 없으면 DB에 저장된 목표 기간 사용
    req_period = request.GET.get("preferred_period", preferred_period)

    user_info = {
        "risk_type": profile.risk_type,
        "required_return": required_return,
    }

    from suggests.services.strategy import determine_recommendation_factors
    factors = determine_recommendation_factors(
        required_return, profile.risk_type, goal.preferred_period
    )
    recommendation_type = factors["final"]

    # 추천 이력 저장
    recommendation_record = Recommendation.objects.create(
        user=user,
        current_asset=goal.current_asset,
        target_asset=goal.target_asset,
        target_years=goal.target_years,
        required_return=required_return,
        total_score=profile.total_score,
        risk_type=profile.risk_type
    )

    if recommendation_type == "예금":
        response = include_factors(_handle_deposit(required_return), factors)

    elif recommendation_type == "예적금 혼합":
        response = include_factors(_handle_deposit_saving(
            required_return, category), factors)

    elif recommendation_type in ["적금 + 주식(안정형)", "적금+주식"]:
        response = include_factors(
            _handle_saving_plus_stock(
                required_return, user_info, selected_market, selected_sector),
            factors
        )

    elif recommendation_type.startswith("주식"):
        response = include_factors(
            _handle_stock_only(required_return, user_info,
                               selected_market, selected_sector),
            factors
        )

    elif recommendation_type.startswith("경고"):
        response = include_factors(
            _handle_warning(required_return, category),
            factors
        )
    else:
        response = Response({"detail": "추천 조건이 일치하지 않습니다."}, status=400)

    # 응답에 추천 ID 추가
    if response.status_code == 200:
        response.data['recommendation_id'] = recommendation_record.id

    return response


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

    # items = get_deposit_saving_recommendations(required_return, category)
    items = get_deposit_saving_recommendations(
        required_return,
        category,
        preferred_period=int(req_period)
    )
    if not items:
        return Response({
            "recommendation_type": "예적금",
            "required_return": required_return,
            "preferred_period": int(req_period),
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
