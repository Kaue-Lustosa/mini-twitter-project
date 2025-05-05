from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import app_settings, api_root, root_redirect

schema_view = get_schema_view(
   openapi.Info(
      title="Mini Twitter API",
      default_version='v1',
      description="A simple social media platform API",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@minitwitter.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    # Root URL redirects to API root
    path('', root_redirect, name='root'),
    
    # API root
    path('api/', api_root, name='api-root'),
    
    # Admin URLs
    path('admin/', admin.site.urls),
    
    # API endpoints
    path('api/users/', include('users.urls')),
    path('api/posts/', include('posts.urls')),
    path('api/notifications/', include('notifications.urls')),
    path('api/direct-messages/', include('direct_messages.urls')),
    path('api/settings/', app_settings, name='app-settings'),
    
    # Swagger documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
