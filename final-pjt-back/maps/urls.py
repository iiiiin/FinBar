from django.urls import path
from . import views

urlpatterns = [
    path("", views.resolve_map_location),
    path("search_bank/", views.search_nearby_places),
]
