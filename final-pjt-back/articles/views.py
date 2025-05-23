from django.shortcuts import render
from .models import Article, Comment
from django.http import JsonResponse
from rest_framework.decorators import api_view


@api_view(['GET', 'POST'])
def article_list(request):
    if request.method == "GET":
        pass
