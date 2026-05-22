# dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_home, name='home'),
    path('get-more/', views.get_more_analyses, name='get_more_analyses'),  # Add this for infinite scroll
]