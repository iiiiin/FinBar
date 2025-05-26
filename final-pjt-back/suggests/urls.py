from django.urls import path
from . import views

urlpatterns = [
    path("questions/", views.get_investment_questions),
    path("submit/", views.submit_investment_answers),
]
