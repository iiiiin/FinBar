from .models import Article, Comment

from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication

from .serializers import ArticleListSerializer, ArticleSerializer
# from .serializers import CommentListSerializer, CommentSerializer

# =====================
#        게시글
# =====================

# 게시글 목록 조회 / 누구나


@api_view(['GET', "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_list(request):
    if request.method == "GET":
        articles = get_list_or_404(Article)
        serializer = ArticleListSerializer(articles, many=True)

        return Response(serializer.data)

    # 게시글 생성 / 로그인 사용자
    elif request.method == "POST":
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# @authentication_classes([TokenAuthentication])
# @permission_classes([IsAuthenticated])
# def create_article(request):


@api_view(['GET', 'DELETE', 'PUT'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def article_detail(request, article_pk):

    # 댓글 수 필요 시 여기 서 annotate와 시리얼라이저 수정
    article = get_object_or_404(Article, pk=article_pk)

    # 단일 게시글 조회
    if request.method == "GET":
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    # 게시글 삭제
    if request.method == "DELETE":
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 게시글 수정 / 일부 수정 허용
    if request.method == "PUT":
        serializer = ArticleSerializer(
            article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)

# =====================
#        댓글
# =====================
