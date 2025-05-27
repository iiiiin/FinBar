from financial_products.models import DepositProduct, SavingProduct
from django.db.models import F
from django.db.models.functions import Abs

RISK_LEVEL_ALLOW_LIST = ["low", "medium"]


def _get_top_product_recommendations(
    model,
    related_name: str,
    label: str,
    required_return: float,
    limit: int = 6,
    option_limit: int = 3,
    preferred_period: int = None
) -> list:
    """
    상품 모델에서 수익률과 가까운 옵션을 기준으로 추천 리스트 생성

    :param model: Django 모델 (DepositProduct, SavingProduct)
    :param related_name: related_name (예: depositproductoptions)
    :param label: 반환될 타입/카테고리 라벨 (예: "예금", "적금")
    :param required_return: 목표 수익률
    :param limit: 상품 추천 개수 제한
    :param option_limit: 각 상품당 옵션 추천 개수 제한
    :return: 추천 상품 리스트
    """
    result = []

    qs = model.objects.prefetch_related(related_name).filter(
        risk_level__in=RISK_LEVEL_ALLOW_LIST
    )

    for product in qs:
        opts = getattr(product, related_name).filter(
            intr_rate2__isnull=False,
            **({"save_trm": preferred_period} if preferred_period else {})
        )
        # 목표 수익률과의 절댓값 차이로 정렬
        options = sorted(
            opts,
            key=lambda o: abs(o.intr_rate2 - required_return)
        )
        if not options.exists():
            continue

        top_options = sorted(
            options,
            key=lambda o: abs(o.intr_rate2 - required_return)
        )[:option_limit]

        result.append({
            "type": label,
            "name": product.fin_prdt_nm,
            "bank": product.kor_co_nm,
            "product_code": product.fin_prdt_cd,
            "category": label,
            "options": [
                {"save_trm": o.save_trm, "intr_rate2": o.intr_rate2}
                for o in top_options
            ]
        })

    return result[:limit]

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


def get_deposit_only_recommendations(required_return: float, limit: int = 6):
    return _get_top_product_recommendations(
        model=DepositProduct,
        related_name="depositproductoptions",
        label="예금",
        required_return=required_return,
        limit=limit
    )


def get_saving_only_recommendations(required_return: float, limit: int = 6):
    return _get_top_product_recommendations(
        model=SavingProduct,
        related_name="savingproductoptions",  # 실제 모델에서 related_name 확인 필요
        label="적금",
        required_return=required_return,
        limit=limit
    )


def get_deposit_saving_recommendations(required_return, category=None):
    result = []

    if category in ["예금", None]:
        result += get_deposit_only_recommendations(required_return)

    if category in ["적금", None]:
        result += get_saving_only_recommendations(required_return)

    return result[:6]  # 총 6개로 제한 (혼합일 경우 예금/적금 합산)
