from django.conf import settings
from django.db import models
from django.utils import timezone


class Site(models.Model):
    class SiteType(models.TextChoices):
        WEBSITE = 'website', 'Website'
        API = 'api', 'API'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sites')
    name = models.CharField(max_length=200)
    url = models.URLField()
    client_name = models.CharField(max_length=200, blank=True)
    site_type = models.CharField(max_length=20, choices=SiteType.choices, default=SiteType.WEBSITE)
    is_active = models.BooleanField(default=True, help_text='Current up/down status as of last check')
    monitoring_enabled = models.BooleanField(default=True, help_text='If false, monitoring is paused')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.url})"


class SiteStatusHistory(models.Model):
    STATUS_UP = 'up'
    STATUS_DOWN = 'down'
    STATUS_CHOICES = [
        (STATUS_UP, 'Up'),
        (STATUS_DOWN, 'Down'),
    ]

    site = models.ForeignKey(Site, on_delete=models.CASCADE, related_name='history')
    timestamp = models.DateTimeField(default=timezone.now, db_index=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    response_time = models.IntegerField(null=True, blank=True, help_text='Response time in ms')

    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['site', 'timestamp']),
            models.Index(fields=['site', 'status', 'timestamp']),
        ]

    def __str__(self):
        return f"{self.site.name} {self.status} at {self.timestamp}"


class DeviceToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='device_tokens')
    token = models.CharField(max_length=512, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    platform = models.CharField(max_length=50, blank=True, help_text='ios|android|web')
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user} - {self.platform}"