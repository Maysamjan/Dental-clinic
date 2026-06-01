from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Role, Doctor, UserSession

User = get_user_model()


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "code", "name", "permissions", "is_system"]


class DoctorSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.full_name", read_only=True)

    class Meta:
        model = Doctor
        fields = [
            "id", "user", "name", "specialization",
            "license_number", "working_hours", "is_active",
        ]


class UserSerializer(serializers.ModelSerializer):
    role_code = serializers.CharField(source="role.code", read_only=True)
    role_name = serializers.CharField(source="role.name", read_only=True)
    permissions = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "full_name", "phone",
            "role", "role_code", "role_name", "permissions",
            "is_active", "password", "date_joined",
        ]
        read_only_fields = ["date_joined"]

    def get_permissions(self, obj):
        return obj.role.permissions if obj.role else []

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k, v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


class MeSerializer(UserSerializer):
    """Serializer for the authenticated user's own profile."""

    class Meta(UserSerializer.Meta):
        read_only_fields = ["date_joined", "username", "role"]


class ClinicTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Embeds role/permissions in the JWT and the login response body."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role_code
        token["full_name"] = user.full_name
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = UserSerializer(self.user).data
        return data


class UserSessionSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserSession
        fields = [
            "id", "user", "username", "ip_address",
            "user_agent", "login_at", "logout_at", "is_active",
        ]
