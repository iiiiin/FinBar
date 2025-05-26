# pagination.py
from rest_framework.pagination import PageNumberPagination


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10  # 기본값
    page_query_param = 'page'  # ex: ?page=2
    page_size_query_param = 'limit'  # ex: ?limit=5
    max_page_size = 100  # 최대 허용 개수
