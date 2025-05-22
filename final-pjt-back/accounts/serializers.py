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
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.save()
        return user


class CustomUserDetailsSerializer(UserDetailsSerializer):
    age = serializers.IntegerField(required=True)
    nickname = serializers.CharField(max_length=150, required=True)
    username = serializers.CharField(read_only=True)  # username은 읽기 전용
    email = serializers.EmailField(required=True)

    class Meta(UserDetailsSerializer.Meta):
        model = get_user_model()
        fields = UserDetailsSerializer.Meta.fields + ("email", "age", "nickname")
        read_only_fields = ("username",)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance
