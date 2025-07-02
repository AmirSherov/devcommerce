from django.urls import path
from . import views

app_name = 'ai_generator'

urlpatterns = [
    # Единственный endpoint для AI генерации
    path('smart-generate/', views.SmartAIGenerationView.as_view(), name='smart_generate'),
    
    # История и статистика
    path('history/', views.AIGenerationHistoryView.as_view(), name='history'),
    path('limits/', views.GetUserLimitsView.as_view(), name='user_limits'),
    path('stats/', views.AIStatsView.as_view(), name='ai_stats'),
    
    # Шаблоны промптов
    path('templates/', views.PromptTemplatesView.as_view(), name='prompt_templates'),
] 