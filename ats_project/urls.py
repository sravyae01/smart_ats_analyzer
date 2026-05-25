from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse

def home(request):
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
    path('', home, name='home'),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('analyzer/', include('analyzer.urls')),
]