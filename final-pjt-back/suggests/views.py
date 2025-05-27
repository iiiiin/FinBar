# suggests/views.py
import logging
from investment_profile.models import InvestmentGoal, InvestmentProfile
from financial_products.serializers import (
    ProductRecommendationSerializer,
    DepositSavingRecommendationResponseSerializer,
)
from suggests.services.strategy import determine_recommendation_factors
from .services.openai_client import (
    build_stock_prompt,
    ask_gpt_for_product_recommendation,
)
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.utils import timezone

from investment_profile.serializers import InvestmentGoalSerializer
from .models import (
    InvestmentQuestion,
    InvestmentChoice,
    Recommendation,
    StockRecommendation,
)
from .serializers import (
    InvestmentQuestionSerializer,
    InvestmentAnswerSerializer,
    StockRecommendationCreateSerializer,
    StockRecommendationSaveSerializer,
)
from suggests.services.temp import _get_top_product_recommendations
from suggests.services.temp import (
    get_deposit_only_recommendations,
    get_saving_only_recommendations,
    get_deposit_saving_recommendations,
)

# 로거 설정
logger = logging.getLogger("suggests")

RISK_LEVEL = {
    "안정형": ["low"],
    "안정추구형": ["low", "medium"],
    "위험중립형": ["medium"],
    "적극투자형": ["medium", "high"],
    "공격투자형": ["high"],
}

MARKET_CHOICES = ["KOSPI", "KOSDAQ", "KONEX"]
SECTOR_CHOICES = [
    "반동체",
    "바이오",
    "2차전지",
    "자동차",
    "금융",
    "건설",
    "에너지",
    "유통",
    "플랫폼",
    "기타",
]


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_investment_questions(request):
    """
    투자 성향 진단 질문을 조회합니다.
    캐시를 사용하여 성능을 최적화합니다.
    """
    cache_key = f"investment_questions_{request.user.id}"
    cached_data = cache.get(cache_key)

    if cached_data:
        logger.debug(
            f"[get_investment_questions] 캐시된 데이터 반환: {request.user.username}"
        )
        return Response(cached_data)

    try:
        # N+1 문제 해결을 위한 select_related와 prefetch_related 사용
        questions = InvestmentQuestion.objects.prefetch_related(
            Prefetch(
                "choices",
                queryset=InvestmentChoice.objects.only(
                    "id", "content", "score", "question_id"
                ),
            )
        ).only("id", "content", "order")

        serializer = InvestmentQuestionSerializer(questions, many=True)
        response_data = serializer.data

        # 캐시에 저장 (1시간)
        cache.set(cache_key, response_data, 3600)

        logger.debug(
            f"[get_investment_questions] 새로운 데이터 조회 및 캐시: {request.user.username}"
        )
        return Response(response_data)
    except Exception as e:
        logger.error(f"[get_investment_questions] 데이터 조회 실패: {str(e)}")
        return Response({"error": "질문 데이터를 불러오는데 실패했습니다."}, status=500)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_investment_answers(request):
    """
    투자 성향 진단 답변을 제출하고 결과를 반환합니다.
    캐시 무효화를 포함합니다.
    """
    try:
        logger.debug(
            f"[submit_investment_answers] 사용자: {request.user.username}, 요청 데이터: {request.data}"
        )

        serializer = InvestmentAnswerSerializer(data=request.data)
        if not serializer.is_valid():
            logger.error(
                f"[submit_investment_answers] 유효성 검사 실패: {serializer.errors}"
            )
            return Response(
                {"error": "Invalid data format", "details": serializer.errors},
                status=400,
            )

        answers = serializer.validated_data["answers"]
        if not answers:
            logger.error("[submit_investment_answers] 답변이 제공되지 않음")
            return Response({"error": "No answers provided"}, status=400)

        # 벌크 쿼리로 선택지 조회
        choice_ids = [ans.get("choice_id") for ans in answers]
        choices = InvestmentChoice.objects.filter(id__in=choice_ids).select_related(
            "question"
        )

        # 선택지 ID를 키로 하는 딕셔너리 생성
        choices_dict = {choice.id: choice for choice in choices}

        total_score = sum(choices_dict[ans["choice_id"]].score for ans in answers)

        # 점수에 따른 위험 유형 결정
        risk_type = (
            "안정형"
            if total_score <= 7
            else (
                "안정추구형"
                if total_score <= 11
                else (
                    "위험중립형"
                    if total_score <= 15
                    else "적극투자형" if total_score <= 19 else "공격투자형"
                )
            )
        )

        # 프로필 업데이트 또는 생성
        profile, created = InvestmentProfile.objects.update_or_create(
            user=request.user,
            defaults={
                "total_score": total_score,
                "risk_type": risk_type,
                "evaluated_at": timezone.now(),
            },
        )

        # 관련 캐시 무효화
        cache.delete(f"investment_questions_{request.user.id}")
        cache.delete(f"investment_profile_{request.user.id}")

        response_data = {
            "risk_type": profile.risk_type,
            "total_score": profile.total_score,
            "evaluated_at": profile.evaluated_at,
        }

        logger.info(
            f"[submit_investment_answers] 성공: {request.user.username}, 위험 유형: {risk_type}"
        )
        return Response(response_data)

    except Exception as e:
        logger.exception(f"[submit_investment_answers] 예상치 못한 오류: {str(e)}")
        return Response({"error": f"Unexpected error: {str(e)}"}, status=500)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def save_recommended_stocks(request):
    """
    주식 추천 결과를 저장하는 API 엔드포인트
    """
    logger = logging.getLogger(__name__)
    logger.debug(
        f"[save_recommended_stocks] 사용자: {request.user.username}, 요청 데이터: {request.data}"
    )

    serializer = StockRecommendationCreateSerializer(
        data=request.data, many=True, context={"request": request}
    )
    if serializer.is_valid():
        serializer.save()
        logger.info(
            f"[save_recommended_stocks] 사용자 {request.user.username}의 추천 종목 저장 성공"
        )
        return Response({"message": "추천 종목 저장 완료"}, status=201)
    logger.error(f"[save_recommended_stocks] 유효성 검사 실패: {serializer.errors}")
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
    logger.warning(
        f"[investment_goal_view] 사용자 {request.user.username}가 deprecated API 호출"
    )
    return Response(
        {
            "message": "이 API는 deprecated 되었습니다.",
            "new_endpoints": {
                "get": "/api/investment-profile/goal/",
                "create": "/api/investment-profile/goal/create/",
                "update": "/api/investment-profile/goal/",
            },
        },
        status=status.HTTP_410_GONE,
    )


def parse_required_return_param(request):
    """공통된 required_return 파라미터 처리"""
    required_return = request.GET.get("required_return")
    if not required_return:
        logger.error("[parse_required_return_param] required_return 파라미터 누락")
        return None, Response(
            {"error": "required_return 필드가 필요합니다."}, status=400
        )
    try:
        return float(required_return), None
    except ValueError:
        logger.error(
            f"[parse_required_return_param] 잘못된 required_return 값: {required_return}"
        )
        return None, Response({"error": "올바른 수익률을 입력해주세요."}, status=400)


def _is_stock_investment_available(profile, required_return: float) -> bool:
    """
    사용자의 투자 성향과 필요 수익률을 기반으로 주식 투자 가능 여부를 결정합니다.
    """
    if profile.risk_type in ["적극투자형", "공격투자형"]:
        return required_return > 5.0
    elif profile.risk_type == "위험중립형":
        return required_return > 7.0
    return False


def _determine_recommendation_type(profile, required_return: float) -> str:
    """
    사용자의 투자 성향과 필요 수익률을 기반으로 추천 유형을 결정합니다.
    """
    logger = logging.getLogger(__name__)

    # 위험 유형에 따른 추천 유형 결정
    if profile.risk_type == "안정형":
        if required_return <= 3.0:
            return "예금"
        elif required_return <= 4.0:
            return "예금+적금"
        elif required_return <= 5.0:
            return "적금"
        else:
            logger.warning(
                f"[_determine_recommendation_type] 안정형 사용자의 높은 목표 수익률: {required_return}%"
            )
            return "경고"
    elif profile.risk_type == "안정추구형":
        if required_return <= 3.5:
            return "예금"
        elif required_return <= 4.5:
            return "예금+적금"
        elif required_return <= 6.0:
            return "적금"
        else:
            logger.warning(
                f"[_determine_recommendation_type] 안정추구형 사용자의 높은 목표 수익률: {required_return}%"
            )
            return "경고"
    elif profile.risk_type == "위험중립형":
        if required_return <= 4.0:
            return "예금+적금"
        elif required_return <= 7.0:
            return "적금"
        else:
            return "주식"
    elif profile.risk_type in ["적극투자형", "공격투자형"]:
        if required_return <= 5.0:
            return "적금"
        else:
            return "주식"
    else:
        logger.warning(
            f"[_determine_recommendation_type] 알 수 없는 위험 유형: {profile.risk_type}"
        )
        return "예금"  # 기본값


def _get_recommendation_factors(
    profile, required_return: float, preferred_period: int = None
) -> dict:
    """
    추천에 사용된 요소들을 반환합니다.
    """
    return {
        "by_return": _determine_recommendation_type(profile, required_return),
        "by_risk": profile.risk_type,
        "final": _determine_recommendation_type(profile, required_return),
        "preferred_period": preferred_period,
    }


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def investment_product_recommendation_view(request):
    """투자 상품 추천 API"""
    logger = logging.getLogger(__name__)

    # 사용자 정보 가져오기
    user = request.user
    try:
        goal = user.investment_goal
        profile = user.investment_profile
        required_return = goal.calculate_required_return()

        logger.info(
            f"[investment_product_recommendation_view] 사용자: {user.username}, 필요 수익률: {required_return}, 위험 유형: {profile.risk_type}"
        )

        # 주식 투자 가능 여부 확인
        is_stock_available = _is_stock_investment_available(profile, required_return)
        logger.info(
            f"[investment_product_recommendation_view] 주식 투자 가능 여부: {is_stock_available}"
        )

        # 추천 유형 결정
        recommendation_type = _determine_recommendation_type(profile, required_return)
        factors = _get_recommendation_factors(
            profile, required_return, goal.preferred_period
        )
        factors["is_stock_available"] = is_stock_available  # 주식 투자 가능 여부 추가

        logger.debug(
            f"[investment_product_recommendation_view] 추천 유형: {recommendation_type}, 요소: {factors}"
        )

        # 추천 처리
        if recommendation_type == "예금":
            response = _handle_deposit(
                request, required_return, factors.get("preferred_period")
            )
        elif recommendation_type == "적금":
            response = _handle_saving(request, required_return)
        elif recommendation_type == "예금+적금":
            response = _handle_deposit_saving(request, required_return)
        elif recommendation_type == "경고":
            response = _handle_warning(request, required_return, profile)
        else:  # 주식
            response = _handle_stock_only(request, profile, goal)

        # 응답에 요소 추가
        response.data["factors"] = factors
        logger.debug(
            f"[investment_product_recommendation_view] 응답 데이터: {response.data}"
        )
        return response

    except InvestmentGoal.DoesNotExist:
        logger.error(
            f"[investment_product_recommendation_view] 사용자 {user.username}의 투자 목표 정보 없음"
        )
        return Response({"error": "투자 목표 정보가 없습니다."}, status=400)
    except InvestmentProfile.DoesNotExist:
        logger.error(
            f"[investment_product_recommendation_view] 사용자 {user.username}의 투자 성향 정보 없음"
        )
        return Response({"error": "투자 성향 정보가 없습니다."}, status=400)
    except Exception as e:
        logger.exception(
            f"[investment_product_recommendation_view] 예외 발생: {str(e)}"
        )
        return Response({"error": str(e)}, status=500)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def deposit_only_recommendation_view(request):
    logger.debug(
        f"[deposit_only_recommendation_view] 사용자: {request.user.username}, 요청 파라미터: {request.GET}"
    )
    required_return, error = parse_required_return_param(request)
    if error:
        return error

    response = _handle_deposit(request, required_return)
    logger.debug(f"[deposit_only_recommendation_view] 응답 데이터: {response.data}")
    return response


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def saving_only_recommendation_view(request):
    logger.debug(
        f"[saving_only_recommendation_view] 사용자: {request.user.username}, 요청 파라미터: {request.GET}"
    )
    required_return, error = parse_required_return_param(request)
    if error:
        return error

    response = _handle_saving(request, required_return)
    logger.debug(f"[saving_only_recommendation_view] 응답 데이터: {response.data}")
    return response


# 🔽 핸들러 함수 분리


def _handle_deposit(request, required_return: float, preferred_period: int = None):
    """예금 상품 추천 처리"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"[_handle_deposit] 필요 수익률: {required_return}, 선호 기간: {preferred_period}"
    )

    items = get_deposit_only_recommendations(
        required_return=required_return, preferred_period=preferred_period
    )

    if not items:
        logger.info(
            f"[_handle_deposit] 조건을 만족하는 예금 상품 없음 (필요 수익률: {required_return}, 선호 기간: {preferred_period})"
        )
        return Response(
            {
                "recommendation_type": "예금",
                "required_return": required_return,
                "preferred_period": preferred_period,
                "message": "조건을 만족하는 예금 상품이 없습니다.",
                "items": [],
            }
        )

    return Response(
        {
            "recommendation_type": "예금",
            "required_return": required_return,
            "preferred_period": preferred_period,
            "items": items,
        }
    )


def _handle_saving(request, required_return: float):
    logger = logging.getLogger(__name__)
    logger.info(f"[_handle_saving] 필요 수익률: {required_return}")

    items = get_saving_only_recommendations(required_return)

    if not items:
        logger.info(
            f"[_handle_saving] 조건을 만족하는 적금 상품 없음 (필요 수익률: {required_return})"
        )
        return Response(
            {
                "recommendation_type": "적금",
                "required_return": required_return,
                "message": "조건을 만족하는 적금 상품이 없습니다.",
                "items": [],
            }
        )

    serializer = ProductRecommendationSerializer(items, many=True)
    logger.debug(f"[_handle_saving] 추천 상품 수: {len(items)}")
    return Response(
        {
            "recommendation_type": "적금",
            "required_return": required_return,
            "items": serializer.data,
        }
    )


def _handle_deposit_saving(request, required_return: float):
    logger = logging.getLogger(__name__)
    logger.debug(f"[_handle_deposit_saving] 필요 수익률: {required_return}")

    items = get_deposit_saving_recommendations(
        required_return, preferred_period=int(req_period)
    )
    if not items:
        logger.info(
            f"[_handle_deposit_saving] 조건을 만족하는 예적금 상품 없음 (필요 수익률: {required_return})"
        )
        return Response(
            {
                "recommendation_type": "예적금",
                "required_return": required_return,
                "preferred_period": int(req_period),
                "message": "조건을 만족하는 예금/적금 상품이 없습니다.",
                "items": [],
            }
        )

    serializer = DepositSavingRecommendationResponseSerializer(
        {
            "recommendation_type": "예적금",
            "required_return": required_return,
            "items": items,
        }
    )
    logger.debug(f"[_handle_deposit_saving] 추천 상품 수: {len(items)}")
    return Response(serializer.data)


def _handle_stock_only(request, profile, goal):
    logger = logging.getLogger(__name__)
    required_return = (
        profile.required_return
        if hasattr(profile, "required_return")
        else goal.calculate_required_return()
    )
    market_choice = request.GET.get("market", "KOSPI")  # 기본값으로 KOSPI 설정
    sector_choice = request.GET.get("sector", "반도체")  # 기본값으로 반도체 설정

    logger.debug(
        f"[_handle_stock_only] 필요 수익률: {required_return}, 사용자 정보: {profile.risk_type}, 시장: {market_choice}, 섹터: {sector_choice}"
    )

    try:
        # OpenAI API를 통한 주식 추천
        prompt = build_stock_prompt(profile, market_choice, sector_choice)
        response = ask_gpt_for_product_recommendation(prompt)

        if not response:
            return Response(
                {
                    "message": "주식 추천을 받을 수 없습니다.",
                    "recommendation_type": "주식",
                    "required_return": required_return,
                    "items": [],
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        return Response(
            {
                "recommendation_type": "주식",
                "required_return": required_return,
                "items": response,
                "factors": _get_recommendation_factors(
                    profile, required_return, goal.preferred_period
                ),
            }
        )

    except Exception as e:
        logger.error(f"[_handle_stock_only] 예외 발생: {str(e)}")
        return Response(
            {
                "message": "주식 추천을 받을 수 없습니다.",
                "recommendation_type": "주식",
                "required_return": required_return,
                "items": [],
            }
        )


def _handle_warning(request, required_return: float, profile):
    """경고 메시지 처리"""
    logger = logging.getLogger(__name__)
    logger.info(
        f"[_handle_warning] 필요 수익률: {required_return}, 위험 유형: {profile.risk_type}"
    )

    # 위험 유형별 경고 메시지
    if profile.risk_type == "안정형":
        message = "현재 안정형 투자 성향으로는 목표 수익률 달성이 어렵습니다. 투자 성향을 재평가하거나 목표 수익률을 조정하는 것을 고려해 보세요."
    elif profile.risk_type == "안정추구형":
        message = "현재 안정추구형 투자 성향으로는 목표 수익률 달성이 어렵습니다. 투자 성향을 재평가하거나 목표 수익률을 조정하는 것을 고려해 보세요."
    else:
        message = "현재 투자 성향으로는 목표 수익률 달성이 어렵습니다. 투자 성향을 재평가하거나 목표 수익률을 조정하는 것을 고려해 보세요."

    return Response(
        {
            "recommendation_type": "경고",
            "required_return": required_return,
            "message": message,
            "items": [],
            "warning": True,
        }
    )


def include_factors(response, factors):
    if isinstance(response, Response):
        response.data["factors"] = factors
    return response


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_saved_recommendations(request):
    """
    사용자가 저장한 추천 상품 목록을 조회합니다.
    현재는 주식 추천만 지원합니다.
    """
    logger.debug(f"[get_saved_recommendations] 사용자: {request.user.username}")
    try:
        stocks = StockRecommendation.objects.filter(user=request.user)
        serializer = StockRecommendationSaveSerializer(stocks, many=True)
        logger.debug(f"[get_saved_recommendations] 저장된 추천 수: {len(stocks)}")
        return Response(serializer.data)
    except Exception as e:
        logger.exception(f"[get_saved_recommendations] 저장된 추천 조회 실패: {str(e)}")
        return Response({"error": f"저장된 추천 조회 실패: {str(e)}"}, status=500)


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_saved_recommendation(request, recommendation_id):
    """
    저장된 추천 상품을 삭제합니다.
    """
    logger.info(
        f"삭제 요청 - 사용자: {request.user.username}, 추천 ID: {recommendation_id}"
    )

    try:
        # 추천 상품이 존재하는지 확인
        recommendation = StockRecommendation.objects.filter(
            id=recommendation_id, user=request.user
        ).first()

        if not recommendation:
            logger.warning(
                f"삭제 실패 - 추천 상품을 찾을 수 없음 (ID: {recommendation_id})"
            )
            return Response(
                {"error": "추천 상품을 찾을 수 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 삭제 수행
        recommendation.delete()
        logger.info(f"삭제 성공 - 추천 ID: {recommendation_id}")

        return Response(
            {"message": "추천 상품이 삭제되었습니다."}, status=status.HTTP_200_OK
        )

    except StockRecommendation.DoesNotExist:
        logger.warning(f"삭제 실패 - 존재하지 않는 추천 상품 (ID: {recommendation_id})")
        return Response(
            {"error": "존재하지 않는 추천 상품입니다."},
            status=status.HTTP_404_NOT_FOUND,
        )
    except Exception as e:
        logger.error(f"삭제 중 오류 발생: {str(e)}")
        return Response(
            {"error": "추천 상품 삭제 중 오류가 발생했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )


@api_view(["DELETE"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def delete_all_saved_recommendations(request):
    """
    사용자의 모든 저장된 추천 상품을 삭제합니다.
    """
    logger.info(f"전체 삭제 요청 - 사용자: {request.user.username}")

    try:
        # 삭제할 추천 상품 수 확인
        count = StockRecommendation.objects.filter(user=request.user).count()

        if count == 0:
            logger.info(
                f"전체 삭제 - 삭제할 추천 상품 없음 (사용자: {request.user.username})"
            )
            return Response(
                {"message": "삭제할 추천 상품이 없습니다."}, status=status.HTTP_200_OK
            )

        # 삭제 수행
        StockRecommendation.objects.filter(user=request.user).delete()
        logger.info(f"전체 삭제 성공 - 삭제된 추천 상품 수: {count}")

        return Response(
            {"message": f"{count}개의 추천 상품이 삭제되었습니다."},
            status=status.HTTP_200_OK,
        )

    except Exception as e:
        logger.error(f"전체 삭제 중 오류 발생: {str(e)}")
        return Response(
            {"error": "추천 상품 삭제 중 오류가 발생했습니다."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
