"""
URL configuration for logsinout project.

Routes URLs to views. For more information:
https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include

# ✅ These are needed to serve media files during development
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('loging.urls')),  # Main app
    path('auth_access/', include('useraccess.urls')),  # Authentication app
]

# ✅ Serve media files (e.g., uploaded images) during development only
# This allows access to files under MEDIA_ROOT at MEDIA_URL
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# ✅ CORRECTIONS & NOTES:
# - No changes in logic needed — your usage of static() is already perfect.
# - Always wrap static() in `if settings.DEBUG:` to avoid issues in production.
# - Ensure MEDIA_URL is defined in settings.py as '/media/' (which we've fixed).
