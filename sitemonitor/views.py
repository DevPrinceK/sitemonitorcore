import logging
from datetime import timedelta
from django.db.models import Avg, Count, Q
from django.utils import timezone
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from knox.models import AuthToken
from .models import Site, SiteStatusHistory, DeviceToken
from .serializers import (
    SiteSerializer, SiteStatusHistorySerializer, DeviceTokenSerializer,
    RegisterSerializer, UserSerializer
)
from .permissions import IsOwnerOrReadOnly

logger = logging.getLogger(__name__)


class SiteViewSet(viewsets.ModelViewSet):
    serializer_class = SiteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return Site.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['post'], url_path='toggle-monitoring')
    def toggle_monitoring(self, request, pk=None):
        site = self.get_object()
        site.monitoring_enabled = not site.monitoring_enabled
        site.save(update_fields=['monitoring_enabled'])
        return Response({'monitoring_enabled': site.monitoring_enabled})

    @action(detail=True, methods=['get'], url_path='stats')
    def stats(self, request, pk=None):
        site = self.get_object()
        period = request.query_params.get('period', 'daily')
        now = timezone.now()
        if period == 'weekly':
            since = now - timedelta(days=7)
        elif period == 'monthly':
            since = now - timedelta(days=30)
        else:
            since = now - timedelta(days=1)

        qs = site.history.filter(timestamp__gte=since)
        total = qs.count() or 1
        up = qs.filter(status='up').count()
        down = qs.filter(status='down').count()
        avg_resp = qs.aggregate(avg=Avg('response_time'))['avg']
        uptime_pct = (up / total) * 100
        downtime_pct = (down / total) * 100
        return Response({
            'period': period,
            'from': since,
            'to': now,
            'uptime_percentage': round(uptime_pct, 2),
            'downtime_percentage': round(downtime_pct, 2),
            'average_response_time_ms': avg_resp,
            'checks': total,
        })


class SiteStatusHistoryViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = SiteStatusHistorySerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return SiteStatusHistory.objects.filter(site__owner=self.request.user)


class DeviceTokenViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = DeviceTokenSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DeviceToken.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save()
    token = AuthToken.objects.create(user)[1]
    return Response({
        'user': UserSerializer(user).data,
        'token': token
    }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    sites = Site.objects.filter(owner=request.user)
    total = sites.count()
    up = sites.filter(is_active=True).count()
    down = sites.filter(is_active=False).count()
    last_24h = timezone.now() - timedelta(days=1)
    checks = SiteStatusHistory.objects.filter(site__in=sites, timestamp__gte=last_24h)
    avg_response = checks.aggregate(avg=Avg('response_time'))['avg']

    return Response({
        'total_sites': total,
        'up': up,
        'down': down,
        'uptime_percentage_last_24h': round((checks.filter(status='up').count() / (checks.count() or 1)) * 100, 2),
        'average_response_time_ms_last_24h': avg_response,
    })
