from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, SiteStatusHistoryViewSet, DeviceTokenViewSet

router = DefaultRouter()
router.register(r'sites', SiteViewSet, basename='site')
router.register(r'history', SiteStatusHistoryViewSet, basename='history')
router.register(r'device-tokens', DeviceTokenViewSet, basename='device-token')

urlpatterns = router.urls
