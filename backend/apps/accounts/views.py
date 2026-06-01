from django.contrib.auth import get_user_model
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.core.permissions import HasModulePermission
from apps.audit.utils import log_activity
from .models import Role, Doctor, UserSession
from .serializers import (
    RoleSerializer, DoctorSerializer, UserSerializer, MeSerializer,
    ClinicTokenObtainPairSerializer, UserSessionSerializer,
)

User = get_user_model()


def client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")


class LoginView(TokenObtainPairView):
    """JWT login that records a session and an audit entry."""

    serializer_class = ClinicTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            username = request.data.get("username")
            user = User.objects.filter(username=username).first()
            if user:
                ip = client_ip(request)
                user.last_login_ip = ip
                user.save(update_fields=["last_login_ip"])
                UserSession.objects.create(
                    user=user,
                    ip_address=ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
                )
                log_activity(user, "LOGIN", "User", user.id, "User logged in", ip)
        return response


class MeViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        return Response(MeSerializer(request.user).data)

    @action(detail=False, methods=["post"])
    def logout(self, request):
        UserSession.objects.filter(user=request.user, is_active=True).update(
            is_active=False
        )
        log_activity(request.user, "LOGOUT", "User", request.user.id, "User logged out")
        return Response(status=status.HTTP_204_NO_CONTENT)


class RoleViewSet(viewsets.ModelViewSet):
    module = "roles"
    permission_classes = [HasModulePermission]
    queryset = Role.objects.all()
    serializer_class = RoleSerializer


class UserViewSet(viewsets.ModelViewSet):
    module = "users"
    permission_classes = [HasModulePermission]
    queryset = User.objects.select_related("role").all()
    serializer_class = UserSerializer
    search_fields = ["username", "full_name", "email", "phone"]
    filterset_fields = ["role", "is_active"]


class DoctorViewSet(viewsets.ModelViewSet):
    module = "users"
    permission_classes = [HasModulePermission]
    queryset = Doctor.objects.select_related("user").all()
    serializer_class = DoctorSerializer
    filterset_fields = ["is_active", "specialization"]

    # Doctors list is readable by clinical roles even without users.view.
    def get_permissions(self):
        if self.action in ("list", "retrieve"):
            return [IsAuthenticated()]
        return super().get_permissions()


class UserSessionViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    module = "audit"
    permission_classes = [HasModulePermission]
    queryset = UserSession.objects.select_related("user").all()
    serializer_class = UserSessionSerializer
    filterset_fields = ["user", "is_active"]
