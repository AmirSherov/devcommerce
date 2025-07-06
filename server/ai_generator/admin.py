from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    TemplateAIGeneration, TemplateAIStats, 
    GlobalTemplateAIStats
)


@admin.register(TemplateAIGeneration)
class TemplateAIGenerationAdmin(admin.ModelAdmin):
    """
    🤖 АДМИНКА ДЛЯ AI ГЕНЕРАЦИЙ ШАБЛОНОВ
    """
    
    list_display = [
        'id', 'user_link', 'template_link', 'project_title', 
        'status_badge', 'response_time', 'created_at'
    ]
    
    list_filter = [
        'status', 'template__category', 'created_at', 
        'template__is_premium'
    ]
    
    search_fields = [
        'user__username', 'user__email', 'template__title',
        'project_title', 'project_description'
    ]
    
    readonly_fields = [
        'id', 'user', 'template', 'duration', 'created_at', 
        'started_at', 'completed_at', 'ai_raw_response'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'user', 'template', 'status')
        }),
        ('Данные проекта', {
            'fields': ('project_title', 'project_description', 'user_data')
        }),
        ('Результат', {
            'fields': ('portfolio_created', 'original_html', 'generated_html')
        }),
        ('Метрики', {
            'fields': ('response_time', 'tokens_used', 'duration')
        }),
        ('Отладка', {
            'fields': ('error_message', 'ai_raw_response'),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Ссылка на пользователя"""
        if obj.user:
            url = reverse('admin:authentication_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'Пользователь'
    
    def template_link(self, obj):
        """Ссылка на шаблон"""
        if obj.template:
            url = reverse('admin:portfolio_templates_portfoliotemplate_change', args=[obj.template.pk])
            return format_html('<a href="{}">{}</a>', url, obj.template.title)
        return '-'
    template_link.short_description = 'Шаблон'
    
    def status_badge(self, obj):
        """Бейдж статуса"""
        colors = {
            'processing': '#ffc107',
            'success': '#28a745',
            'failed': '#dc3545',
            'ai_error': '#fd7e14',
            'invalid_html': '#e83e8c',
            'server_overload': '#6f42c1'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="color: white; background-color: {}; padding: 2px 8px; border-radius: 4px; font-size: 12px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Статус'


@admin.register(TemplateAIStats)
class TemplateAIStatsAdmin(admin.ModelAdmin):
    """
    📊 АДМИНКА ДЛЯ СТАТИСТИКИ AI
    """
    
    list_display = [
        'user_link', 'date', 'ai_requests_count', 'ai_successful_count',
        'ai_success_rate_display', 'regular_usage_count', 'total_usage_display'
    ]
    
    list_filter = [
        'date', 'ai_requests_count', 'ai_successful_count'
    ]
    
    search_fields = ['user__username', 'user__email']
    
    readonly_fields = [
        'user', 'date', 'ai_success_rate', 'total_usage', 
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'date')
        }),
        ('AI статистика', {
            'fields': (
                'ai_requests_count', 'ai_successful_count', 'ai_failed_count',
                'ai_success_rate'
            )
        }),
        ('Обычное использование', {
            'fields': ('regular_usage_count', 'total_usage')
        }),
        ('Метрики производительности', {
            'fields': ('total_ai_response_time', 'total_tokens_used')
        }),
        ('Дополнительно', {
            'fields': ('popular_templates', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Ссылка на пользователя"""
        if obj.user:
            url = reverse('admin:authentication_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'Пользователь'
    
    def ai_success_rate_display(self, obj):
        """Отображение процента успеха"""
        rate = obj.ai_success_rate
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 50 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    ai_success_rate_display.short_description = 'Успешность AI'
    
    def total_usage_display(self, obj):
        """Общее использование"""
        return f"{obj.total_usage} (AI: {obj.ai_requests_count}, Обычно: {obj.regular_usage_count})"
    total_usage_display.short_description = 'Общее использование'


@admin.register(GlobalTemplateAIStats)
class GlobalTemplateAIStatsAdmin(admin.ModelAdmin):
    """
    🌍 АДМИНКА ДЛЯ ГЛОБАЛЬНОЙ СТАТИСТИКИ
    """
    
    list_display = [
        'date', 'total_ai_requests', 'total_ai_successful', 
        'ai_success_rate_display', 'active_ai_users', 'total_regular_usage'
    ]
    
    list_filter = ['date']
    
    readonly_fields = [
        'ai_vs_regular_ratio', 'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Дата', {
            'fields': ('date',)
        }),
        ('AI метрики', {
            'fields': (
                'total_ai_requests', 'total_ai_successful', 'total_ai_failed',
                'average_ai_response_time', 'total_tokens_consumed'
            )
        }),
        ('Пользователи', {
            'fields': ('active_ai_users', 'premium_users_count')
        }),
        ('Обычное использование', {
            'fields': ('total_regular_usage', 'ai_vs_regular_ratio')
        }),
        ('Популярные данные', {
            'fields': (
                'popular_templates_ai', 'popular_templates_regular', 
                'error_distribution'
            ),
            'classes': ('collapse',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def ai_success_rate_display(self, obj):
        """Отображение глобального процента успеха"""
        if obj.total_ai_requests == 0:
            return '0%'
        
        rate = (obj.total_ai_successful / obj.total_ai_requests) * 100
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 50 else '#dc3545'
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color, rate
        )
    ai_success_rate_display.short_description = 'Успешность AI' 