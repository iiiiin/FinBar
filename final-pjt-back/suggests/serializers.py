from .models import StockRecommendation
from rest_framework import serializers
from .models import InvestmentQuestion, InvestmentChoice
from accounts.models import InvestmentGoal


class InvestmentChoiceSerializer(serializers.ModelSerializer):
    """
    [목적]
    - 각 투자 질문(InvestmentQuestion)에 대한 선택지(InvestmentChoice)를 직렬화합니다.
    - 사용자가 선택할 수 있는 보기(choice_text)와 내부 점수(score)를 제공합니다.
    - 이 serializer는 InvestmentQuestionSerializer 내부에서 중첩 형태로 사용됩니다.

    [사용처]
    - 프론트엔드에 질문과 함께 각 선택지를 전달할 때 사용됩니다.
    - 사용자 응답 제출 시 선택된 choice_id 값을 기준으로 점수를 산정합니다.
    """
    class Meta:
        model = InvestmentChoice
        fields = ("id", "choice_text", "score")


class InvestmentQuestionSerializer(serializers.ModelSerializer):
    """
    [목적]
    - 투자 성향 설문 질문(InvestmentQuestion)과 관련된 선택지 목록을 포함해 직렬화합니다.
    - 중첩된 InvestmentChoiceSerializer를 통해 각 질문에 대한 보기 리스트도 함께 반환합니다.

    [사용처]
    - 설문지 화면 구성 시, 질문과 선택지를 함께 프론트로 전송하는 API 응답에 사용됩니다.
    - GET suggets/questions/ API의 응답 형식을 구성합니다.
    """
    choices = InvestmentChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = InvestmentQuestion
        fields = ("id", "question_text", "choices")


class InvestmentAnswerSerializer(serializers.Serializer):
    """
    사용자가 제출한 답변을 처리하기 위한 serializer
    {"answers": [{"question_id": 1, "choice_id": 3}, ...]}
    """
    answers = serializers.ListField(
        child=serializers.DictField(
            child=serializers.IntegerField()
        )
    )

    def validate_answers(self, value):
        seen = set()
        for ans in value:
            qid = ans.get("question_id")
            cid = ans.get("choice_id")
            if qid is None or cid is None:
                raise serializers.ValidationError(
                    "question_id와 choice_id는 모두 필요합니다.")
            if qid in seen:
                raise serializers.ValidationError(f"질문 ID {qid}에 중복 응답이 있습니다.")
            seen.add(qid)
        return value


# suggests/serializers.py


class StockRecommendationSaveSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRecommendation
        fields = ("id", "name", "code", "market",
                  "sector", "reason", "recommended_at")


class StockRecommendationCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = StockRecommendation
        fields = ("name", "code", "market", "sector", "reason")

    def create(self, validated_data):
        user = self.context["request"].user
        return StockRecommendation.objects.create(user=user, **validated_data)
