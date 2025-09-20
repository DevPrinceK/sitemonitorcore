from django.contrib import admin
from .models import Site, SiteStatusHistory, DeviceToken


@admin.register(Site)
class SiteAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "url", "client_name", "site_type", "is_active", "monitoring_enabled", "owner", "created_at")
    list_filter = ("site_type", "is_active", "monitoring_enabled", "created_at")
    search_fields = ("name", "url", "client_name", "owner__username")
    raw_id_fields = ("owner",)


@admin.register(SiteStatusHistory)
class SiteStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ("id", "site", "status", "response_time", "timestamp")
    list_filter = ("status", "timestamp")
    search_fields = ("site__name", "site__url")
    raw_id_fields = ("site",)


@admin.register(DeviceToken)
class DeviceTokenAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "platform", "active", "created_at")
    list_filter = ("platform", "active", "created_at")
    search_fields = ("user__username", "token")
    raw_id_fields = ("user",)
