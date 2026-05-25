from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # Landing page is ALWAYS the root URL
    path('', TemplateView.as_view(template_name='landing.html'), name='landing'),
    # Accounts URLs (login, signup, logout)
    path('accounts/', include('accounts.urls')),  # ← Removed duplicate '', added 'accounts/'
    path('dashboard/', include('dashboard.urls')),
    path('analyzer/', include('analyzer.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)