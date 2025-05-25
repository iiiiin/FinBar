# services.py
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

# API 엔드포인트 분리
DEPOSIT_API_URL = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
SAVING_API_URL  = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"


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
    base_list   = first.get("baseList", [])
    option_list = first.get("optionList", [])
    max_page    = first.get("max_page_no", 1)

    for page in range(2, max_page + 1):
        page_data = _fetch_page(api_url, top_fin_grp_no, page)
        base_list.extend(page_data.get("baseList", []))
        option_list.extend(page_data.get("optionList", []))

    return base_list, option_list

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
    cols  = list(records[0].keys())
    values = [[rec[col] for col in cols] for rec in records]

    insert_sql = f"""
    INSERT INTO {table} ({','.join(cols)})
    VALUES %s
    ON CONFLICT ({','.join(unique_fields)})
    DO UPDATE SET
      {', '.join(f"{f}=EXCLUDED.{f}" for f in update_fields)};
    """

    with transaction.atomic():
        with connection.cursor() as cur:
            execute_values(cur, insert_sql, values)




# ─── Deposit 전용 Upsert ───

def upsert_deposit_products(model, data_list: list[dict]):
    base_recs = []
    for item in data_list:
        base_recs.append({
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

    _upsert_generic(
        model=model,
        unique_fields=["fin_prdt_cd"],
        update_fields=[f for f in base_recs[0] if f != "fin_prdt_cd"],
        records=base_recs
    )


def upsert_deposit_options(data_list: list[dict]):
    opt_recs = []
    for opt in data_list:
        # (1) ForeignKey에 실제 DepositProduct.id를 매핑하는 로직이 필요할 수 있습니다.
        opt_recs.append({
            "deposit_product_id": opt["fin_prdt_cd"],  
            "intr_rate_type_nm":  opt["intr_rate_type_nm"],
            "save_trm":           opt["save_trm"],
            "intr_rate":          opt["intr_rate"],
            "intr_rate2":         opt["intr_rate2"],
        })

    _upsert_generic(
        model=DepositProductOptions,
        # (2) deposit_product_id를 포함해서 상품별로 중복 허용
        unique_fields=["deposit_product_id", "intr_rate_type_nm", "save_trm"],
        update_fields=["intr_rate", "intr_rate2"],
        records=opt_recs
    )

# ─── Saving 전용 Upsert ───

def upsert_saving_products(model, data_list: list[dict]):
    # DepositProduct와 필드 구조 동일 → 같은 함수 재사용
    upsert_deposit_products(model, data_list)




def upsert_saving_options(data_list: list[dict]):
    opt_recs = []
    for opt in data_list:
        opt_recs.append({
            "saving_product_id": opt["fin_prdt_cd"],
            "intr_rate_type_nm": opt["intr_rate_type_nm"],
            "rsrv_type_nm":      opt["rsrv_type_nm"],
            "save_trm":           opt["save_trm"],
            "intr_rate":          opt["intr_rate"],
            "intr_rate2":         opt["intr_rate2"],
        })

    _upsert_generic(
        model=SavingProductOptions,
        unique_fields=["saving_product_id", "intr_rate_type_nm", "save_trm"],
        update_fields=["rsrv_type_nm", "intr_rate", "intr_rate2"],
        records=opt_recs
    )

# ─── 전체 수집 & Upsert 트리거 ───

def fetch_and_upsert_deposit(top_fin_grp_no: str):
    base, opts = _collect_all(DEPOSIT_API_URL, top_fin_grp_no)
    upsert_deposit_products(DepositProduct, base)
    upsert_deposit_options(opts)


def fetch_and_upsert_saving(top_fin_grp_no: str):
    base, opts = _collect_all(SAVING_API_URL, top_fin_grp_no)
    upsert_saving_products(SavingProduct, base)
    upsert_saving_options(opts)
