from .models import Stock
from django.shortcuts import render
from datetime import datetime
import sys
import csv
from rest_framework.response import Response

# from rest_framework import
from rest_framework.decorators import api_view


# DB 데이터 저장용 함수
# @api_view(["GET"])
# def upload_stocks(request):

#     sys.stdin = open("C:/Users/pc/Desktop/stocks.csv", "r", encoding="UTF8")

#     data = list(csv.reader(sys.stdin))

#     for row in data[1:]:
#         stock = Stock()
#         stock.stock_code = row[1]
#         stock.stock_name = row[2]
#         stock.stock_name_en = row[4]
#         converted_date = datetime.strptime(row[5], "%Y/%m/%d").strftime("%Y-%m-%d")
#         stock.first_trade_date = converted_date
#         stock.market = row[6]
#         stock.security_type = row[7]
#         stock.market_division = row[8]
#         stock.stock_type = row[9]
#         if row[10] != "무액면":
#             stock.face_value = row[10]
#         else:
#             stock.face_value = None
#         stock.listed_shares = row[11]
#         stock.save()
#     return Response({})
