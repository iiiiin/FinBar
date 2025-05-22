from django.db import models
from django.contrib.auth.models import AbstractUser
# from allauth.account.models import EmailAddress


class User(AbstractUser):
    age = models.PositiveIntegerField(null=False)
    nickname = models.CharField(max_length=150, null=False)



# class CustomEmailAddress(EmailAddress):
#     class Meta:
#         proxy = False  # proxy 아님
#         # db_table = 'account_emailaddress'  # 기존 테이블과 동일하게 유지할 경우
#         constraints = []
