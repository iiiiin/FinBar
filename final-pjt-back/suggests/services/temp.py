from financial_products.models import DepositProduct, SavingProduct
from django.db.models import F
from django.db.models.functions import Abs
import logging
from django.db.models import Prefetch
from typing import List, Dict

RISK_LEVEL_ALLOW_LIST = ["low", "medium", "high"]


def _get_top_product_recommendations(
    required_return: float,
    preferred_period: int = None,
    risk_level: str = None,
    product_type: str = "deposit",
) -> List[Dict]:
    """
    상품 추천을 위한 공통 함수
    """
    logger = logging.getLogger(__name__)
    logger.info(
        f"[_get_top_product_recommendations] 필요 수익률: {required_return}, 선호 기간: {preferred_period}, 위험도: {risk_level}"
    )

    # 상품 유형에 따른 모델과 related_name 설정
    if product_type == "deposit":
        model = DepositProduct
        related_name = "depositproductoptions"
        category = "예금"
    else:  # saving
        model = SavingProduct
        related_name = "savingproductoptions"
        category = "적금"

    # 옵션 모델 가져오기
    option_model = model._meta.get_field(related_name).related_model

    # 최적화된 쿼리 실행
    products = (
        model.objects.filter(
            risk_level=risk_level if risk_level else "low",
            **{f"{related_name}__intr_rate2__isnull": False},
            **{f"{related_name}__intr_rate2__gt": 0},
            **(
                {f"{related_name}__save_trm": preferred_period}
                if preferred_period
                else {}
            ),
        )
        .annotate(min_rate_diff=Abs(F(f"{related_name}__intr_rate2") - required_return))
        .filter(
            **{f"{related_name}__intr_rate2__gte": required_return - 0.5},
            **{f"{related_name}__intr_rate2__lte": required_return + 0.5},
        )
        .order_by("min_rate_diff")
        .prefetch_related(
            Prefetch(
                related_name,
                queryset=option_model.objects.filter(
                    intr_rate2__isnull=False,
                    intr_rate2__gt=0,
                    **({"save_trm": preferred_period} if preferred_period else {}),
                )
                .annotate(rate_diff=Abs(F("intr_rate2") - required_return))
                .order_by("rate_diff")
                .only("intr_rate2", "save_trm", "intr_rate_type_nm"),
            )
        )
        .only(
            "id",
            "fin_prdt_nm",
            "kor_co_nm",
            "fin_prdt_cd",
        )
    )[
        :10
    ]  # 상위 10개 가져오기 (중복 제거 후 5개가 남도록)

    # 결과 처리
    result = []
    seen_products = set()  # 이미 처리한 상품을 추적 (은행명 + 상품명)

    for product in products:
        # 은행명과 상품명을 조합하여 고유 키 생성
        product_key = f"{product.kor_co_nm}_{product.fin_prdt_nm}"

        if product_key in seen_products:
            continue

        options = getattr(product, related_name).all()
        if options.exists():
            # 가장 적합한 옵션 하나만 선택
            best_option = options.first()
            result.append(
                {
                    "type": category,
                    "name": product.fin_prdt_nm,
                    "bank": product.kor_co_nm,
                    "product_code": product.fin_prdt_cd,
                    "category": category,
                    "options": [
                        {
                            "save_trm": best_option.save_trm,
                            "intr_rate2": best_option.intr_rate2,
                            "intr_rate_type_nm": best_option.intr_rate_type_nm,
                        }
                    ],
                }
            )
            seen_products.add(product_key)

        # 5개 상품이 모이면 중단
        if len(result) >= 5:
            break

    logger.info(f"[_get_top_product_recommendations] 필터링된 상품 수: {len(result)}")
    return result


# def _get_top_product_recommendations(
#     model,
#     related_name: str,
#     label: str,
#     required_return: float,
#     limit: int = 6,
#     option_limit: int = 3
# ) -> list:
#     from django.db.models import Prefetch

#     result = []

#     qs = model.objects.prefetch_related(
#         Prefetch(
#             related_name,
#             queryset=None  # 아래에서 필터링 처리
#         )
#     ).filter(
#         risk_level__in=RISK_LEVEL_ALLOW_LIST
#     )

#     for product in qs:
#         options = getattr(product, related_name).filter(
#             intr_rate2__isnull=False,
#             save_trm=12,   # 12개월만
#         ).annotate(
#             diff=Abs(F('intr_rate2') - required_return)
#         ).order_by('diff')[:option_limit]
#         # options = getattr(product, related_name).filter(
#         #     intr_rate2__isnull=False,
#         #     intr_rate2__gte=required_return,  # ✅ 수익률 필터링
#         # ).order_by("-intr_rate2")  # ✅ 높은 수익률 우선

#         if not options.exists():
#             continue

#         top_options = options[:option_limit]

#         result.append({
#             "type": label,
#             "name": product.fin_prdt_nm,
#             "bank": product.kor_co_nm,
#             "product_code": product.fin_prdt_cd,
#             "category": label,
#             "options": [
#                 {"save_trm": o.save_trm, "intr_rate2": o.intr_rate2}
#                 for o in top_options
#             ]
#         })

#     return result[:limit]


def get_deposit_only_recommendations(
    required_return: float, limit: int = 6, preferred_period: int = None
):
    return _get_top_product_recommendations(
        required_return=required_return,
        preferred_period=preferred_period,
        risk_level="low",  # 예금은 low risk
    )


def get_saving_only_recommendations(required_return: float, limit: int = 6):
    return _get_top_product_recommendations(
        required_return=required_return,
        risk_level="medium",  # 적금은 medium risk
    )


def get_deposit_saving_recommendations(required_return, category=None):
    result = []

    if category in ["예금", None]:
        result += get_deposit_only_recommendations(required_return)

    if category in ["적금", None]:
        result += get_saving_only_recommendations(required_return)

    return result[:6]  # 총 6개로 제한 (혼합일 경우 예금/적금 합산)
