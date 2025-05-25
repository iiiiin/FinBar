from django.urls import path
from . import views

urlpatterns = [
    path("", views.keyword_search),
    path("mark/", views.mark_video),
    path("marked/", views.marked_video)
]

