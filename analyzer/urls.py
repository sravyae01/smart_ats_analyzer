# analyzer/urls.py - COMPLETE WORKING VERSION WITH AI CHAT
from django.urls import path
from . import views

app_name = 'analyzer'

urlpatterns = [
    # Analysis URLs
    path('new/', views.new_analysis, name='new'),
    path('upload/', views.upload_and_analyze, name='upload'),
    path('results/<uuid:analysis_id>/', views.results_view, name='results'),
    path('history/', views.history_view, name='history'),
    path('api/analysis/<uuid:analysis_id>/', views.get_analysis_data, name='api_analysis'),
    
    # AI Chat Assistant URLs
    path('chat/', views.chat_view, name='chat'),
    path('chat/ask/', views.chat_ask, name='chat_ask'),
]