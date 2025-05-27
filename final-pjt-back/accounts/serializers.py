from allauth.account.utils import setup_user_email
from allauth.account.models import EmailAddress
from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import UserDetailsSerializer

from rest_framework import serializers
from allauth.account.adapter import get_adapter
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth import get_user_model


class CustomRegisterSerializer(RegisterSerializer):
    age = serializers.IntegerField(required=True)
    nickname = serializers.CharField(required=True)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data["age"] = self.validated_data.get("age")
        data["nickname"] = self.validated_data.get("nickname", "")
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()

        # 기본 필드 설정
        user = adapter.save_user(request, user, self, commit=False)

        # 커스텀 필드 설정
        user.age = self.cleaned_data.get("age")
        user.nickname = self.cleaned_data.get("nickname")

        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(
                    self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    age = serializers.IntegerField(required=True)
    nickname = serializers.CharField(max_length=150, required=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=True)

    class Meta(UserDetailsSerializer.Meta):
        model = get_user_model()
        fields = UserDetailsSerializer.Meta.fields + \
            ("email", "age", "nickname")
        read_only_fields = ("username",)

    def update(self, instance, validated_data):
        # 1) 이메일이 바뀌었으면 allauth 유틸로 처리
        new_email = validated_data.get("email")
        if new_email and new_email != instance.email:
            # 1-1) 실제 User.email 갱신
            instance.email = new_email
            instance.save()
            # 1-2) EmailAddress도 동기화 (기존 기본 이메일을 업데이트)
            EmailAddress.objects.filter(
                user=instance, primary=True).update(email=new_email)
        # 2) 나머지 필드
        instance.age = validated_data.get("age", instance.age)
        instance.nickname = validated_data.get("nickname", instance.nickname)
        instance.save()
        return instance
