from .views import deposit_companies, saving_companies
from django.urls import path
from rest_framework.routers import DefaultRouter
from .views import DepositProductViewSet, SavingProductViewSet

router = DefaultRouter()
router.register(r'deposits',
                DepositProductViewSet, basename='deposit')
router.register(r'savings', SavingProductViewSet, basename='saving')

urlpatterns = router.urls


urlpatterns += [
    path("products/deposits/companies/",
         deposit_companies, name="deposit-companies"),
    path("products/savings/companies/",
         saving_companies, name="saving-companies"),
]
