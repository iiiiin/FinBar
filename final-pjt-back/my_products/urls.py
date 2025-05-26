# urls.py (앱 내부)
from rest_framework.routers import DefaultRouter
from .views import DepositBookmarkViewSet, SavingBookmarkViewSet, StockBookmarkViewSet

router = DefaultRouter()
router.register(r"deposits", DepositBookmarkViewSet, basename="deposit-bookmarks")
router.register(r"savings", SavingBookmarkViewSet, basename="saving-bookmarks")
router.register(r"stocks", StockBookmarkViewSet, basename="stock-bookmarks")

urlpatterns = router.urls
