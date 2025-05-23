from rest_framework import serializers
from .models import Article, Comment
from django.contrib.auth import get_user_model


class ArticleListSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField(source='user.nickname')

    class Meta:
        model = Article
        fields = ('title', 'content', 'user', 'nickname', 'created_at')


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('id', 'user')


# class ArticleDetailSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Article
#         fields = '__all__'
#         read_only_fields = ('id', 'user')


class CommentListSerializer(serializers.ModelSerializer):
    nickname = serializers.ReadOnlyField(source='user.nickname')

    class Meta:
        model = Article
        fields = ('article', 'content', 'user', 'nickname', 'created_at')


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'
        read_only_fields = ('id', 'article', 'user')
