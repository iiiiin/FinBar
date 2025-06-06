from .models import Article, Comment

from django.shortcuts import get_object_or_404, get_list_or_404

from rest_framework.response import Response
from rest_framework.decorators import (
    api_view,
    permission_classes,
    authentication_classes,
)
from rest_framework import status
from rest_framework.permissions import (
    IsAuthenticated,
    AllowAny,
    IsAuthenticatedOrReadOnly,
)
from rest_framework.authentication import TokenAuthentication

from .serializers import ArticleListSerializer, ArticleSerializer
from .serializers import CommentListSerializer, CommentSerializer

# =====================
#        게시글
# =====================


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
def article_list(request):
    # 게시글 목록 조회 / 누구나(읽기 전용)
    if request.method == "GET":
        articles = Article.objects.all()
        serializer = ArticleListSerializer(articles, many=True)
        return Response(serializer.data)

    # 게시글 생성 (로그인 필요)
    elif request.method == "POST":
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = ArticleSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE", "PUT"])
@authentication_classes([TokenAuthentication])
def article_detail(request, article_pk):
    article = get_object_or_404(Article, pk=article_pk)

    # 단일 게시글 조회 (누구나 가능)
    if request.method == "GET":
        serializer = ArticleSerializer(article)
        return Response(serializer.data)

    # 게시글 삭제 (로그인 필요)
    if request.method == "DELETE":
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        article.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 게시글 수정 (로그인 필요)
    if request.method == "PUT":
        if not request.user.is_authenticated:
            return Response(
                {"detail": "로그인이 필요합니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
        serializer = ArticleSerializer(article, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)


# =====================
#        댓글
# =====================


@api_view(["GET", "POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_list(request, article_pk):

    # 댓글 목록 조회 / 누구나(읽기 전용)
    if request.method == "GET":
        comment_list = get_list_or_404(Comment, article=article_pk)
        serializer = CommentListSerializer(comment_list, many=True)
        return Response(serializer.data)

    # 댓글 수정 (작성자만)
    elif request.method == "POST":
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                article=Article.objects.get(pk=article_pk), user=request.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET", "DELETE", "PUT"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def comment_detail(request, article_pk, comment_pk):
    comment = get_object_or_404(Comment, pk=comment_pk)

    # 단일 댓글 조회 (수정 전 데이터 전달?)
    if request.method == "GET":
        serializer = CommentSerializer(comment)
        return Response(serializer.data)

    # 댓글 삭제
    if request.method == "DELETE":
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    # 댓글 수정
    if request.method == "PUT":
        serializer = CommentSerializer(comment, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save(
                user=request.user, article=Article.objects.get(pk=article_pk)
            )
            return Response(serializer.data)
