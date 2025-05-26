# your_app/management/commands/sync_stocks.py

from django.core.management.base import BaseCommand
from financial_products.services import sync_stock_list


class Command(BaseCommand):
    help = "한국투자증권 API를 통해 주식 종목 정보를 동기화합니다."

    def handle(self, *args, **options):
        try:
            sync_stock_list()
            self.stdout.write(self.style.SUCCESS("✅ 종목 동기화 완료"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ 오류 발생: {e}"))
