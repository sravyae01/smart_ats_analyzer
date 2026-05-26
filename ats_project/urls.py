from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.http import HttpResponse

# Test page (optional - can be deleted)
def test_page(request):
    return HttpResponse("""
        <h1 style="color: green; text-align: center; margin-top: 50px;">
            🚀 Smart ATS Resume Analyzer
        </h1>
        <p style="text-align: center; font-size: 18px;">
            Your Django project is working!
        </p>
        <hr>
        <p style="text-align: center;">
            <a href="/admin/">Admin Panel</a> | 
            <a href="/accounts/login/">Login</a> | 
            <a href="/accounts/signup/">Sign Up</a>
        </p>
    """)

urlpatterns = [
    path('admin/', admin.site.urls),
    # Landing page as homepage (not test page)
    path('', TemplateView.as_view(template_name='landing.html'), name='home'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('analyzer/', include('analyzer.urls')),
    path('test/', test_page, name='test'),  # Optional test page at /test/
]