"""server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
import os
from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="ML Team 2 Service",
        default_version="v0.1.0",
        description="""
      ### Заметки
      Пока нет""",
    ),
    public=True,
    authentication_classes=(),
    url=settings.SWAGGER_SETTINGS["BASE_URL"],
    # permission_classes=[permissions.AllowAny, permissions.IsAuthenticated, IsOwner],
)

path_prefix = os.environ.get("METHODS_PATH_PREFIX", "")

urlpatterns = [
    path("ml-team-2-service/admin/", admin.site.urls),
    path(
        "swagger-ui.html",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path(f"{path_prefix}", include("wineup.urls")),
]
