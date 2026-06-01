from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import (
    LoginView, MeViewSet, RoleViewSet, UserViewSet,
    DoctorViewSet, UserSessionViewSet,
)

router = DefaultRouter()
router.register("roles", RoleViewSet)
router.register("users", UserViewSet)
router.register("doctors", DoctorViewSet)
router.register("sessions", UserSessionViewSet)
router.register("me", MeViewSet, basename="me")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("", include(router.urls)),
]
