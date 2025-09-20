from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from sitemonitor.views import register, dashboard
from sitemonitor.routing import urlpatterns as api_router

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/register/', register, name='register'),
    path('api/auth/', include('knox.urls')),
    path('api/dashboard/', dashboard, name='dashboard'),
    path('api/', include((api_router, 'sitemonitor'), namespace='sitemonitor')),  # routers
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema')), 
    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema')), 
]
