from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # 👥 Registration endpoints
    path("register/resident/", views.register_resident, name="register_resident"),
    path("register/admin/", views.register_admin, name="register_admin"),

    # 🔐 Authentication endpoints
    path("login/resident/", views.login_resident, name="login_resident"),
    path("login/admin/", views.login_admin, name="login_admin"),
    path("logout/", views.logout_user, name="logout_user"),

    # JWT maintenance
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
]
