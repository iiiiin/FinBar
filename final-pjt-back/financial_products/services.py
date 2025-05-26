# services.py
from .models import Stock
import requests
from django.conf import settings
from django.db import connection, transaction
from psycopg2.extras import execute_values
from .models import (
    DepositProduct,
    DepositProductOptions,
    SavingProduct,
    SavingProductOptions,
)

import logging
logger = logging.getLogger(__name__)


# API 엔드포인트 분리
DEPOSIT_API_URL = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
SAVING_API_URL = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"


def _fetch_page(api_url: str, top_fin_grp_no: str, page_no: int) -> dict:
    resp = requests.get(api_url, params={
        "auth":    settings.FINLIFE_API_KEY,
        "topFinGrpNo": top_fin_grp_no,
        "pageNo":  page_no,
    })
    resp.raise_for_status()
    return resp.json()["result"]


def _collect_all(api_url: str, top_fin_grp_no: str):
    """
    모든 페이지에서 baseList, optionList 수집하여 반환
    """
    first = _fetch_page(api_url, top_fin_grp_no, 1)
    base_list = first.get("baseList", [])
    option_list = first.get("optionList", [])
    max_page = first.get("max_page_no", 1)
    top_fin_grp_no = top_fin_grp_no

    logger.info(f"[INFO] max_page_no: {max_page}")

    for page in range(2, max_page + 1):
        logger.info(f"[INFO] page_no: {page}")

        page_data = _fetch_page(api_url, top_fin_grp_no, page)
        base_list.extend(page_data.get("baseList", []))
        option_list.extend(page_data.get("optionList", []))

    return base_list, option_list, top_fin_grp_no


def _upsert_generic(model, unique_fields: list, update_fields: list, records: list[dict]):
    """
    psycopg2 ON CONFLICT Upsert 공통 로직
     - 동일 unique_fields 조합의 레코드는 마지막 값으로 덮어쓰도록 중복 제거
    """
    if not records:
        return

    # 1) unique_fields 기준으로 중복 제거 (마지막 레코드 우선)
    deduped = {}
    for rec in records:
        key = tuple(rec[field] for field in unique_fields)
        deduped[key] = rec
    records = list(deduped.values())

    table = model._meta.db_table
    cols = list(records[0].keys())
    values = [[rec[col] for col in cols] for rec in records]

    insert_sql = f"""
    INSERT INTO {table} ({','.join(cols)})
    VALUES %s
    ON CONFLICT ({','.join(unique_fields)})
    DO UPDATE SET
      {', '.join(f"{f}=EXCLUDED.{f}" for f in update_fields)};
    """

    try:
        with transaction.atomic():
            with connection.cursor() as cur:
                execute_values(cur, insert_sql, values)
    except Exception as e:
        logger.error(f"[ERROR] DB 오류 발생: {e}")


# ─── Deposit 전용 Upsert ───

def upsert_deposit_products(model, data_list: list[dict], fin_no):
    base_recs = []
    for item in data_list:
        try:
            base_recs.append({
                "top_fin_grp_no": fin_no,
                "fin_co_no":     item["fin_co_no"],
                "kor_co_nm":     item["kor_co_nm"],
                "fin_prdt_cd":   item["fin_prdt_cd"],
                "fin_prdt_nm":   item["fin_prdt_nm"],
                "join_way":      item["join_way"],
                "mtrt_int":      item["mtrt_int"],
                "spcl_cnd":      item["spcl_cnd"],
                "join_deny":     item["join_deny"],
                "join_member":   item["join_member"],
                "etc_note":      item["etc_note"],
                "max_limit":     item.get("max_limit"),
                "dcls_strt_day": item["dcls_strt_day"],
            })
        except KeyError as e:
            logger.warning(f"[WARN] fin_prdt_cd 없음: {item.get('fin_prdt_cd')}")

    _upsert_generic(
        model=model,
        unique_fields=["fin_prdt_cd", "fin_co_no"],
        update_fields=[f for f in base_recs[0]
                       if f not in ["fin_prdt_cd", "fin_co_no"]],
        records=base_recs
    )


def upsert_deposit_options(data_list: list[dict]):
    # (1) fin_prdt_cd + fin_co_no → id 매핑
    product_map = {
        (p.fin_prdt_cd, p.fin_co_no): p.id for p in DepositProduct.objects.all()
    }

    opt_recs = []
    for opt in data_list:
        key = (opt["fin_prdt_cd"], opt["fin_co_no"])
        product_id = product_map.get(key)
        if product_id is None:
            logger.warning(f"[WARN] Unknown (fin_prdt_cd, fin_co_no): {key}")
            continue

        opt_recs.append({
            "deposit_product_id": product_id,
            "fin_co_no":          opt["fin_co_no"],  # 추가된 필드
            "intr_rate_type_nm":  opt["intr_rate_type_nm"],
            "save_trm":           opt["save_trm"],
            "intr_rate":          opt["intr_rate"],
            "intr_rate2":         opt["intr_rate2"],
        })

    _upsert_generic(
        model=DepositProductOptions,
        unique_fields=["fin_co_no", "deposit_product_id",
                       "intr_rate_type_nm", "save_trm"],
        update_fields=["intr_rate", "intr_rate2"],
        records=opt_recs
    )

# ─── Saving 전용 Upsert ───


def upsert_saving_products(model, data_list: list[dict], fin_no):
    # DepositProduct와 필드 구조 동일 → 같은 함수 재사용
    upsert_deposit_products(model, data_list, fin_no)


def upsert_saving_options(data_list: list[dict]):
    # (1) fin_prdt_cd + fin_co_no → id 매핑
    product_map = {
        (p.fin_prdt_cd, p.fin_co_no): p.id for p in SavingProduct.objects.all()
    }

    opt_recs = []
    for opt in data_list:
        key = (opt["fin_prdt_cd"], opt["fin_co_no"])
        product_id = product_map.get(key)
        if product_id is None:
            logger.warning(f"[WARN] Unknown (fin_prdt_cd, fin_co_no): {key}")
            continue

        opt_recs.append({
            "saving_product_id":  product_id,
            "fin_co_no":          opt["fin_co_no"],  # 추가된 필드
            "intr_rate_type_nm":  opt["intr_rate_type_nm"],
            "rsrv_type_nm":       opt["rsrv_type_nm"],
            "save_trm":           opt["save_trm"],
            "intr_rate":          opt["intr_rate"],
            "intr_rate2":         opt["intr_rate2"],
        })

    _upsert_generic(
        model=SavingProductOptions,
        unique_fields=["fin_co_no", "saving_product_id",
                       "intr_rate_type_nm", "save_trm", "rsrv_type_nm"],
        update_fields=["intr_rate", "intr_rate2"],
        records=opt_recs
    )

# ─── 전체 수집 & Upsert 트리거 ───


def fetch_and_upsert_deposit(top_fin_grp_no: str):
    base, opts, fin_no = _collect_all(DEPOSIT_API_URL, top_fin_grp_no)
    upsert_deposit_products(DepositProduct, base, fin_no)
    upsert_deposit_options(opts)


def fetch_and_upsert_saving(top_fin_grp_no: str):
    base, opts, fin_no = _collect_all(SAVING_API_URL, top_fin_grp_no)
    upsert_saving_products(SavingProduct, base, fin_no)
    upsert_saving_options(opts)
