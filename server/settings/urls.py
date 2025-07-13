from django.urls import path
from . import views

urlpatterns = [
    # Профиль и основная информация
    path('profile/', views.profile_settings, name='profile_settings'),
    path('avatar/upload/', views.upload_avatar, name='upload_avatar'),
    
    # Настройки уведомлений
    path('notifications/', views.notification_settings, name='notification_settings'),
    
    # Безопасность и сессии
    path('sessions/', views.user_sessions, name='user_sessions'),
    path('sessions/<uuid:session_id>/terminate/', views.terminate_session, name='terminate_session'),
    path('sessions/terminate-all/', views.terminate_all_sessions, name='terminate_all_sessions'),
    path('change-password/', views.change_password, name='change_password'),
    path('sessions/create/', views.create_session_record, name='create_session_record'),
    
    # Обзор всех настроек
    path('overview/', views.settings_overview, name='settings_overview'),
] 