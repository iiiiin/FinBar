from django.urls import path
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'deposits', views.DepositProductViewSet, basename='deposit')
router.register(r'savings',  views.SavingProductViewSet,  basename='saving')

urlpatterns = router.urls