"""
URL configuration for final_pjt project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from django.conf import settings
from django.urls import re_path
from rest_framework.permissions import AllowAny


schema_view = get_schema_view(
    openapi.Info(
        title="Swagger_Practise API",
        default_version="v1",
        description="Swagger Test를 위한 유저 API 문서",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[AllowAny],
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("dj_rest_auth.urls")),
    path("accounts/signup/", include("dj_rest_auth.registration.urls")),
    path("articles/", include("articles.urls")),
    path("products/", include("financial_products.urls")),
    path("youtube/", include("search_youtubes.urls")),
    path("map/", include("maps.urls")),
    path("suggests/", include("suggests.urls")),
    path("bookmarks/", include("my_products.urls")),
    path('investment-profile/', include('investment_profile.urls')),
]


# 디버그일때만 swagger 문서가 보이도록 해주는 설정,
# 여기에 urlpath도 작성 가능해서 debug일때만 작동시킬 api도 설정할 수 있음
if settings.DEBUG:
    urlpatterns += [
        re_path(
            r"^swagger(?P<format>\.json|\.yaml)$",
            schema_view.without_ui(cache_timeout=0),
            name="schema-json",
        ),
        re_path(
            r"^swagger/$",
            schema_view.with_ui("swagger", cache_timeout=0),
            name="schema-swagger-ui",
        ),
        re_path(
            r"^redoc/$",
            schema_view.with_ui("redoc", cache_timeout=0),
            name="schema-redoc",
        ),
    ]

