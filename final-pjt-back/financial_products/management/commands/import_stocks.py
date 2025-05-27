# your_app/management/commands/import_stocks.py
from pathlib import Path
import pandas as pd
from django.core.management.base import BaseCommand
from financial_products.models import Stock
from datetime import datetime


class Command(BaseCommand):
    help = "CSV 파일에서 주식 종목 정보를 불러와 Stock 모델에 저장합니다."

    def add_arguments(self, parser):
        parser.add_argument("csv_file", type=str, help="불러올 CSV 파일 경로")

    def handle(self, *args, **options):
        csv_path = Path("financial_products/static/stocks.csv")  # 고정 경로 사용
        df = pd.read_csv(csv_path)

        count = 0
        for _, row in df.iterrows():
            try:
                액면가_raw = str(row["액면가"]).strip()
                face_value = None
                if 액면가_raw not in ["무액면", "", "nan", "NaN"]:
                    try:
                        face_value = float(액면가_raw)
                    except ValueError:
                        face_value = None  # 혹시 모를 기타 예외 처리

                stock, created = Stock.objects.update_or_create(
                    stock_code=str(row["단축코드"]).zfill(6),
                    defaults={
                        "stock_name": str(row["한글 종목명"]).strip(),
                        "stock_name_en": str(row["영문 종목명"]).strip(),
                        "first_trade_date": datetime.strptime(str(row["상장일"]), "%Y/%m/%d").date(),
                        "market": str(row["시장구분"]).strip() if pd.notna(row["시장구분"]) else "",
                        "security_type": str(row["증권구분"]).strip() if pd.notna(row["증권구분"]) else "",
                        "market_division": str(row.get("소속부", "")).strip() if pd.notna(row.get("소속부", "")) else "",
                        "stock_type": str(row["주식종류"]).strip() if pd.notna(row["주식종류"]) else "",
                        "face_value": face_value,
                        "listed_shares": int(row["상장주식수"]),
                    },
                )

                count += 1
            except Exception as e:
                self.stderr.write(f"❌ {row['단축코드']} 저장 중 오류 발생: {e}")
                continue

        self.stdout.write(self.style.SUCCESS(f"✅ {count}개 종목 저장 완료"))
