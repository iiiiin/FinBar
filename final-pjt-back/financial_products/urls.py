from django.urls import path
from . import views

urlpatterns = [
    # path('add/', views.upload_stocks),
    path('depositProducts/', views.deposit_products),
    path('savingProducts/', views.saving_products),
]
