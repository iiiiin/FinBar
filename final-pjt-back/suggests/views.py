from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework import status

from .models import InvestmentQuestion, InvestmentChoice, InvestmentProfile
from .serializers import InvestmentQuestionSerializer, InvestmentAnswerSerializer


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_investment_questions(request):
    questions = InvestmentQuestion.objects.all()
    serializer = InvestmentQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def submit_investment_answers(request):
    serializer = InvestmentAnswerSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        answers = serializer.validated_data["answers"]
        total_score = 0
        for ans in answers:
            try:
                choice = InvestmentChoice.objects.get(id=ans["choice_id"])
                total_score += choice.score
            except InvestmentChoice.DoesNotExist:
                return Response({"error": "Invalid choice ID"}, status=status.HTTP_400_BAD_REQUEST)

        # 성향 분류 로직
        if total_score <= 7:
            risk_type = "안정형"
        elif total_score <= 11:
            risk_type = "안정추구형"
        elif total_score <= 15:
            risk_type = "위험중립형"
        elif total_score <= 19:
            risk_type = "적극투자형"
        else:
            risk_type = "공격투자형"

        # 저장 or 업데이트
        profile, created = InvestmentProfile.objects.update_or_create(
            user=request.user,
            defaults={
                "total_score": total_score,
                "risk_type": risk_type,
            }
        )
        return Response({
            "risk_type": profile.risk_type,
            "total_score": profile.total_score,
            "evaluated_at": profile.evaluated_at,
        })

    return Response(serializer.errors, status=400)
