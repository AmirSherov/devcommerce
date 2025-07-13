from django.contrib import admin
from .models import UserProfile, UserNotificationSettings, UserSession


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'ip_address', 'is_active', 'session_trusted', 'last_activity']
    list_filter = ['is_active', 'session_trusted', 'last_activity', 'created_at']
    search_fields = ['user__email', 'user__username', 'ip_address']
    readonly_fields = ['session_key', 'jwt_token_hash', 'created_at', 'last_activity']  # first_login_at временно убран
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'session_key', 'jwt_token_hash')
        }),
        ('Устройство', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Статус', {
            'fields': ('is_active', 'session_trusted', 'trusted_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'first_login_at', 'last_activity')
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Записи создаются автоматически


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'location', 'profile_visibility', 'created_at']
    list_filter = ['profile_visibility', 'projects_visibility', 'portfolio_visibility', 'created_at']
    search_fields = ['user__email', 'user__username', 'bio', 'location']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'avatar', 'bio', 'location', 'birth_date', 'gender')
        }),
        ('Социальные ссылки', {
            'fields': ('social_links',)
        }),
        ('Настройки приватности', {
            'fields': ('profile_visibility', 'projects_visibility', 'portfolio_visibility', 'notify_new_followers')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UserNotificationSettings)
class UserNotificationSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'project_notifications', 'created_at']
    list_filter = ['email_notifications', 'project_notifications', 'like_comment_notifications', 'created_at']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Email уведомления', {
            'fields': ('user', 'email_notifications', 'project_notifications', 'like_comment_notifications', 'template_notifications', 'weekly_newsletter')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    ) 