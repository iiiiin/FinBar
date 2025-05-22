from django.db import models
from django.conf import settings
from django.core.validators import MaxLengthValidator


class Article(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    # 게시글 10000자 제한, 폼 유효성 검사 및 db 제한
    content = models.TextField(validators=[MaxLengthValidator(10000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    # 댓글 1000자 제한, 폼 유효성 검사 및 db 제한
    content = models.TextField(validators=[MaxLengthValidator(1000)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
