from .models import Stock
from django.shortcuts import render
from datetime import datetime
import pandas as pd


def upload_stocks(request):

    csv = pd.read_csv(
        "C:/Users/SSAFY/Desktop/final-pjt/final-pjt-back/financial_products/static/stocks.csv")

    print(csv)

    for i in range(2882):
        # stock = Stock()
        data = list(input())
        print(data)
        # stock = Stock()
        # stock.stock_code = data[1]
        # stock.stock_name = data[2]
        # # stock.some_field = data[3]  # 주석 처리된 필드
        # stock.stock_name_en = data[4]
        # converted_date = datetime.strptime(
        #     data[5], "%Y/%m/%d").strftime("%Y-%m-%d")
        # stock.first_trade_date = converted_date
        # stock.market = data[6]
        # stock.security_type = data[7]
        # stock.market_division = data[8]
        # stock.stock_type = data[9]
        # stock.face_value = data[10]
        # stock.listed_shares = data[11]
        # stock.save()
