from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth import get_user_model


class UserInfoMixin(serializers.Serializer):
    nickname = serializers.ReadOnlyField(source="user.nickname")
    username = serializers.ReadOnlyField(source="user.username")


class ArticleListSerializer(UserInfoMixin, serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "content",
            "user",
            "nickname",
            "username",
            "created_at",
        )
        read_only_fields = ("id", "user", "nickname", "username")


class ArticleSerializer(UserInfoMixin, serializers.ModelSerializer):
    comments = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = (
            "id",
            "title",
            "content",
            "user",
            "nickname",
            "username",
            "created_at",
            "updated_at",
            "comments",
        )
        read_only_fields = ("id", "user", "nickname", "username")

    def get_comments(self, obj):
        comments = obj.comment_set.all().order_by("created_at")
        return CommentListSerializer(comments, many=True).data


class CommentListSerializer(UserInfoMixin, serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = (
            "id",
            "article",
            "content",
            "user",
            "nickname",
            "username",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "user", "nickname", "username")


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "article", "content", "user", "created_at", "updated_at")
        read_only_fields = ("id", "user", "article")
