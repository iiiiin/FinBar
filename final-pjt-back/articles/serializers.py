from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth import get_user_model


class ArticleListSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Article
        fields = ("id", "title", "content", "user", "nickname", "created_at")
        read_only_fields = ("id",)


class ArticleSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source="user.username")

    class Meta:
        model = Article
        fields = "__all__"
        read_only_fields = ("id", "user", "username")


class CommentListSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField(source="user.nickname")

    class Meta:
        model = Comment
        fields = (
            "id",
            "article",
            "content",
            "user",
            "nickname",
            "created_at",
            "updated_at",
        )


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"
        read_only_fields = ("id", "article", "user", "nickname")
