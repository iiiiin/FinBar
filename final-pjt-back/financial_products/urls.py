# urls.py
from rest_framework.routers import DefaultRouter
from .views import DepositProductViewSet, SavingProductViewSet
from .views import DepositOptionViewSet, SavingOptionViewSet

router = DefaultRouter()
router.register(r"deposits", DepositProductViewSet, basename="deposits")
router.register(r"savings", SavingProductViewSet, basename="savings")
router.register(r"deposit-options", DepositOptionViewSet, basename="deposit-options")
router.register(r"saving-options", SavingOptionViewSet, basename="saving-options")
urlpatterns = router.urls
