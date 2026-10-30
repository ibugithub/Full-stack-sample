"""
URL configuration for Template project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
import re
from urllib.parse import urlsplit
from django.conf import settings
from django.http import JsonResponse
from django.urls import include, path, re_path
from django.views.decorators.csrf import csrf_exempt
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from .admin_site import configure_admin_site
from .frontend import serve_next_frontend
from users.admin_google import google_callback
from users.google import google_redirect_uri

SchemaView = get_schema_view(
   openapi.Info(
      title=f"{settings.SITE_NAME} API",
      default_version='v1',
      description="API documentation",
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

admin.site.site_header = settings.SITE_NAME
admin.site.site_title = f'{settings.SITE_NAME} Admin'
admin.site.index_title = 'Dashboard'
configure_admin_site(admin.site)


@csrf_exempt  # This fallback only returns 404; it cannot read or modify account data.
def api_not_found(request):
    return JsonResponse({'detail': 'API endpoint not found.'}, status=404)


urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path('api/users/', include('users.urls')),
    path('api/profile/', include('userProfile.urls')),
    # Swagger URLs
    path('swagger<format>/', SchemaView.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', SchemaView.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', SchemaView.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    re_path(r'^api(?:/.*)?$', api_not_found, name='api-not-found'),
    re_path(
        '^' + re.escape(urlsplit(google_redirect_uri()).path.strip('/')) + '/?$',
        google_callback, name='google-oauth-callback',
    ),
    re_path(r'^(?P<path>.*)$', serve_next_frontend, name='next-frontend'),
]
