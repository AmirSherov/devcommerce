from django.urls import path
from .views import (
    TemplateAIGenerateView,
    GetUserAILimitsView,
    TemplateAIStatsView,
    TemplateAIHistoryView,
    track_regular_template_usage
)

app_name = 'ai_generator'

urlpatterns = [
    # 🤖 AI ENDPOINTS ДЛЯ ЗАПОЛНЕНИЯ ШАБЛОНОВ
    
    # AI заполнение конкретного шаблона
    path('templates/<int:template_id>/generate/', 
         TemplateAIGenerateView.as_view(), 
         name='ai_generate_template'),
    
    # Информация о лимитах AI генераций
    path('limits/', 
         GetUserAILimitsView.as_view(), 
         name='ai_limits'),
    
    # Статистика AI использования
    path('stats/', 
         TemplateAIStatsView.as_view(), 
         name='ai_stats'),
    
    # История AI генераций
    path('history/', 
         TemplateAIHistoryView.as_view(), 
         name='ai_history'),
    
    # Учет обычного использования шаблонов
    path('track-regular-usage/', 
         track_regular_template_usage, 
         name='track_regular_usage'),
] 