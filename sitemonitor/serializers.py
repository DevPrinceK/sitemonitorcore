from django.contrib.auth import get_user_model
from rest_framework import serializers
from .models import Site, SiteStatusHistory, DeviceToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]


class SiteSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Site
        fields = [
            "id", "owner", "name", "url", "client_name", "site_type", "is_active", "monitoring_enabled",
            "created_at", "updated_at"
        ]
        read_only_fields = ("is_active", "created_at", "updated_at")


class SiteStatusHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SiteStatusHistory
        fields = ["id", "site", "timestamp", "status", "response_time"]
        read_only_fields = ("timestamp",)


class DeviceTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceToken
        fields = ["id", "token", "platform", "active", "created_at"]
        read_only_fields = ("created_at",)


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("id", "username", "email", "password")

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data.get("email"),
            password=validated_data["password"],
        )
        return user
