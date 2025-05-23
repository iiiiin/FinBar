import sys
import csv
import requests
from datetime import datetime

from .models import Stock
from django.shortcuts import render
from django.conf import settings

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication
from .utils.clean import remove_special_and_space


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

# 예금 상품 조회
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def deposit_products(request):
    API_KEY = settings.FINLIFE_API_KEY
    URL = "http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json"
    financeCd = request.GET.get("financeCd", "")
    clean_financeCd = remove_special_and_space(financeCd).replace("은행", "")

    params = {
        "auth": API_KEY,
        "topFinGrpNo": request.GET.get("topFinGrpNo", "020000"),
        "pageNo": request.GET.get("pageNo", 1),
        "financeCd": clean_financeCd,
    }
    data = requests.get(url=URL, params=params)
    return Response(data.json())


# 적금 상품 조회 
@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([AllowAny])
def saving_products(request):
    API_KEY = settings.FINLIFE_API_KEY
    URL = "http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json"
    financeCd = request.GET.get("financeCd", "")
    clean_financeCd = remove_special_and_space(financeCd).replace("은행", "")

    params = {
        "auth": API_KEY,
        "topFinGrpNo": request.GET.get("topFinGrpNo", "020000"),
        "pageNo": request.GET.get("pageNo", 1),
        "financeCd": clean_financeCd,
    }
    data = requests.get(url=URL, params=params)
    return Response(data.json())
