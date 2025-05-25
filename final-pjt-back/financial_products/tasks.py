import logging
from celery import shared_task
from .services import fetch_and_upsert_deposit, fetch_and_upsert_saving

logger = logging.getLogger(__name__)  # 모듈 이름을 로거 이름으로 사용


@shared_task
def task_upsert_deposit():
    for grp in ("020000", "030300"):
        try:
            fetch_and_upsert_deposit(grp)
        except Exception as e:
            logger.error(f"deposit upsert failed for {grp}: {e}", exc_info=True)


@shared_task
def task_upsert_saving():
    for grp in ("020000", "030300"):
        try:
            fetch_and_upsert_saving(grp)
        except Exception as e:
            logger.error(f"saving upsert failed for {grp}: {e}", exc_info=True)
