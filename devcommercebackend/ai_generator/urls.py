from django.urls import path
from . import views

app_name = 'ai_generator'

urlpatterns = [
    # Основные AI endpoints
    path('generate/', views.ai_generate_portfolio, name='ai_generate_portfolio'),
    path('limits/', views.ai_generation_limits, name='ai_generation_limits'),
    
    # История и статистика пользователя
    path('history/', views.ai_generation_history, name='ai_generation_history'),
    path('stats/', views.ai_user_stats, name='ai_user_stats'),
    path('daily-stats/', views.ai_daily_stats, name='ai_daily_stats'),
    path('style-stats/', views.ai_style_stats, name='ai_style_stats'),
    
    # Шаблоны промптов
    path('templates/', views.ai_prompt_templates, name='ai_prompt_templates'),
    path('templates/save/', views.ai_save_prompt_template, name='ai_save_prompt_template'),
    path('templates/<int:template_id>/delete/', views.ai_delete_prompt_template, name='ai_delete_prompt_template'),
    
    # Административная статистика
    path('global-stats/', views.ai_global_stats, name='ai_global_stats'),
] 