from django.shortcuts import render
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from .models import InvestmentGoal, InvestmentProfile
from .serializers import (
    InvestmentGoalSerializer,
    InvestmentProfileSerializer,
    UserInvestmentProfileSerializer,
)
from django.db import transaction
from rest_framework.exceptions import ValidationError as DRFValidationError

# Create your views here.

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def check_profile_status(request):
    """
    사용자의 투자 프로필 상태를 확인하는 API
    
    Returns:
        {
            "has_investment_profile": bool,  # 투자 성향 프로필 존재 여부
            "has_investment_goal": bool,     # 투자 목표 정보 존재 여부
            "missing_profiles": list         # 없는 프로필 종류 목록
        }
    """
    user = request.user
    has_profile = hasattr(user, 'investment_profile')
    has_goal = hasattr(user, 'investment_goal')
    
    missing = []
    if not has_profile:
        missing.append("investment_profile")
    if not has_goal:
        missing.append("investment_goal")
    
    return Response({
        "has_investment_profile": has_profile,
        "has_investment_goal": has_goal,
        "missing_profiles": missing
    })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_investment_goal(request):
    """새로운 투자 목표를 생성하는 API"""
    try:
        # 요청 데이터 로깅
        print("받은 데이터:", request.data)
        
        # 이미 투자 목표가 있는지 확인
        if hasattr(request.user, 'investment_goal'):
            return Response({
                "error": "이미 투자 목표가 설정되어 있습니다. 수정하려면 PUT 또는 PATCH를 사용하세요.",
                "existing_goal": InvestmentGoalSerializer(request.user.investment_goal).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InvestmentGoalSerializer(data=request.data)
        print("시리얼라이저 데이터:", serializer.initial_data)
        
        if serializer.is_valid():
            print("시리얼라이저 유효성 검사 통과")
            try:
                with transaction.atomic():
                    goal = serializer.save(user=request.user)
                    # 필요 수익률 계산
                    goal.expected_annual_return = goal.calculate_required_return()
                    goal.save()
                    
                    # 계산된 수익률이 너무 높은 경우 경고 메시지 추가
                    response_data = InvestmentGoalSerializer(goal).data
                    if goal.expected_annual_return and goal.expected_annual_return > 30:
                        response_data['warning'] = f"필요 수익률이 {goal.expected_annual_return}%로 매우 높습니다. 현실적인 목표 설정을 권장합니다."
                    
                return Response(response_data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                print("Django 모델 유효성 검사 에러:", str(e))
                return Response({
                    "error": "유효성 검사 실패",
                    "details": str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # 더 자세한 에러 메시지 제공
        print("시리얼라이저 유효성 검사 실패:", serializer.errors)
        errors = serializer.errors
        if 'target_asset' in errors and 'current_asset' in errors:
            errors['general'] = ["목표 자산과 현재 자산을 모두 확인해주세요."]
        
        return Response({
            "error": "입력값이 올바르지 않습니다.",
            "details": errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except DRFValidationError as e:
        print("DRF 유효성 검사 에러:", str(e))
        return Response({
            "error": "유효성 검사 실패",
            "details": str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("예상치 못한 에러:", str(e))
        return Response({
            "error": "투자 목표 생성 중 오류가 발생했습니다.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvestmentGoalAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = InvestmentGoalSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """PUT/PATCH 요청 시 에러 처리 개선"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            
            if serializer.is_valid():
                self.perform_update(serializer)
                # 수익률 재계산
                instance.expected_annual_return = instance.calculate_required_return()
                instance.save()
                
                return Response(serializer.data)
            
            return Response({
                "error": "입력값이 올바르지 않습니다.",
                "details": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                "error": "투자 목표 수정 중 오류가 발생했습니다.",
                "details": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_object(self):
        try:
            return get_object_or_404(InvestmentGoal, user=self.request.user)
        except InvestmentGoal.DoesNotExist:
            raise DRFValidationError({
                "error": "투자 목표가 설정되지 않았습니다. 먼저 투자 목표를 생성해주세요."
            })


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def create_investment_profile(request):
    """새로운 투자 성향 프로필을 생성하는 API"""
    try:
        # 이미 프로필이 있는지 확인
        if hasattr(request.user, 'investment_profile'):
            return Response({
                "error": "이미 투자 성향 프로필이 존재합니다. 수정하려면 PUT 또는 PATCH를 사용하세요.",
                "existing_profile": InvestmentProfileSerializer(request.user.investment_profile).data
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 점수 유효성 검증
        total_score = request.data.get('total_score')
        if total_score is not None:
            if not isinstance(total_score, int) or total_score < 0 or total_score > 25:
                return Response({
                    "error": "총점은 0-25 사이의 정수여야 합니다.",
                    "provided_score": total_score
                }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = InvestmentProfileSerializer(data=request.data)
        if serializer.is_valid():
            with transaction.atomic():
                profile = serializer.save(user=request.user)
            
            return Response(
                InvestmentProfileSerializer(profile).data, 
                status=status.HTTP_201_CREATED
            )
        
        return Response({
            "error": "입력값이 올바르지 않습니다.",
            "details": serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        return Response({
            "error": "투자 성향 프로필 생성 중 오류가 발생했습니다.",
            "details": str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvestmentProfileAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = InvestmentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return super().put(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)

    def get_object(self):
        return get_object_or_404(InvestmentProfile, user=self.request.user)


class UserInvestmentProfileAPIView(generics.RetrieveAPIView):
    serializer_class = UserInvestmentProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_investment_progress(request):
    """투자 목표 달성도를 조회하는 API"""
    try:
        goal = request.user.investment_goal
        
        # 월별 필요 저축액 계산
        days_remaining = goal.get_days_remaining()
        months_remaining = days_remaining / 30 if days_remaining > 0 else 0
        monthly_required = goal.get_remaining_amount() / months_remaining if months_remaining > 0 else 0
        
        return Response({
            "current_asset": goal.current_asset,
            "target_asset": goal.target_asset,
            "progress_percentage": goal.get_progress_percentage(),
            "remaining_amount": goal.get_remaining_amount(),
            "days_remaining": days_remaining,
            "achievement_status": goal.get_achievement_status(),
            "monthly_required_saving": round(monthly_required, 1),
            "expected_annual_return": goal.expected_annual_return
        })
        
    except InvestmentGoal.DoesNotExist:
        return Response({
            "error": "투자 목표가 설정되지 않았습니다."
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['PATCH'])
@authentication_classes([TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def update_current_asset(request):
    """현재 자산만 업데이트하는 API"""
    try:
        goal = request.user.investment_goal
        current_asset = request.data.get('current_asset')
        
        if current_asset is None:
            return Response({
                "error": "current_asset 필드가 필요합니다."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            current_asset = int(current_asset)
            if current_asset < 1:
                raise ValueError("현재 자산은 1만원 이상이어야 합니다.")
        except ValueError as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # 현재 자산 업데이트
        goal.current_asset = current_asset
        goal.expected_annual_return = goal.calculate_required_return()
        goal.save()
        
        # 목표 달성 여부 확인
        if goal.get_progress_percentage() >= 100:
            response_data = InvestmentGoalSerializer(goal).data
            response_data['congratulations'] = "축하합니다! 투자 목표를 달성했습니다!"
            return Response(response_data)
        
        return Response(InvestmentGoalSerializer(goal).data)
        
    except InvestmentGoal.DoesNotExist:
        return Response({
            "error": "투자 목표가 설정되지 않았습니다."
        }, status=status.HTTP_404_NOT_FOUND)
