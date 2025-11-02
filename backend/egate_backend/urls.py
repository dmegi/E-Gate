"""
URL configuration for egate_backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# 📘 Swagger / ReDoc configuration
schema_view = get_schema_view(
    openapi.Info(
        title="E-Gate API Documentation",
        default_version="v1.0",
        description=(
            "Comprehensive REST API documentation for the E-Gate System. "
            "Includes authentication, resident management, event handling, "
            "and QR-based attendance verification."
        ),
        terms_of_service="https://www.adamson.edu.ph/2018/",
        contact=openapi.Contact(email="support@egate.local"),
        license=openapi.License(name="Adamson University License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# ✅ Core API routes
urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),

    # Modular API apps
    path("api/accounts/", include("accounts.urls")),
    path("api/residents/", include("residents.urls")),
    path("api/events/", include("events.urls")),

    # API Documentation (Swagger + ReDoc)
    re_path(
        r"^api/docs(?P<format>\.json|\.yaml)$",
        schema_view.without_ui(cache_timeout=0),
        name="schema-json",
    ),
    path("api/docs/", schema_view.with_ui("swagger", cache_timeout=0), name="schema-swagger-ui"),
    path("api/redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
