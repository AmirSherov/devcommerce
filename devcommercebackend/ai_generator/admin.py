from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Avg, Sum
from django.utils import timezone
from .models import (
    AIGenerationRequest, 
    AIGenerationStats, 
    AIPromptTemplate, 
    GlobalAIStats
)


@admin.register(AIGenerationRequest)
class AIGenerationRequestAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'title', 'status', 'style', 
        'response_time_display', 'created_at', 'portfolio_link'
    ]
    list_filter = [
        'status', 'style', 'created_at', 'user__is_premium'
    ]
    search_fields = [
        'user__username', 'user__email', 'title', 'prompt'
    ]
    readonly_fields = [
        'created_at', 'started_at', 'completed_at', 
        'duration', 'response_time'
    ]
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'title', 'description', 'prompt', 'style')
        }),
        ('Результат', {
            'fields': ('status', 'portfolio_created', 'error_message', 'error_code')
        }),
        ('Технические метрики', {
            'fields': ('response_time', 'tokens_used', 'api_cost')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
        ('Отладка', {
            'fields': ('ai_raw_response',),
            'classes': ('collapse',)
        })
    )
    
    def response_time_display(self, obj):
        if obj.response_time:
            return f"{obj.response_time:.2f}s"
        return "-"
    response_time_display.short_description = "Время ответа"
    
    def portfolio_link(self, obj):
        if obj.portfolio_created:
            return format_html(
                '<a href="/admin/portfolio/portfolio/{}/change/" target="_blank">📁 Портфолио</a>',
                obj.portfolio_created.id
            )
        return "-"
    portfolio_link.short_description = "Портфолио"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'portfolio_created'
        )


@admin.register(AIGenerationStats)
class AIGenerationStatsAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'date', 'requests_count', 'successful_count', 
        'success_rate_display', 'average_response_time_display'
    ]
    list_filter = ['date', 'user__is_premium']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['success_rate', 'average_response_time']
    
    def success_rate_display(self, obj):
        return f"{obj.success_rate}%"
    success_rate_display.short_description = "Успешность"
    
    def average_response_time_display(self, obj):
        return f"{obj.average_response_time}s"
    average_response_time_display.short_description = "Среднее время"


@admin.register(AIPromptTemplate)
class AIPromptTemplateAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'user', 'category', 'style', 'usage_count', 
        'success_rate_display', 'is_public', 'is_featured'
    ]
    list_filter = [
        'category', 'style', 'is_public', 'is_featured', 'created_at'
    ]
    search_fields = ['name', 'prompt', 'user__username']
    list_editable = ['is_public', 'is_featured']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'name', 'prompt', 'category', 'style')
        }),
        ('Статистика', {
            'fields': ('usage_count', 'success_rate'),
            'classes': ('collapse',)
        }),
        ('Настройки', {
            'fields': ('is_public', 'is_featured')
        })
    )
    
    def success_rate_display(self, obj):
        return f"{obj.success_rate:.1f}%"
    success_rate_display.short_description = "Успешность"


@admin.register(GlobalAIStats)
class GlobalAIStatsAdmin(admin.ModelAdmin):
    list_display = [
        'date', 'total_requests', 'total_successful', 
        'success_rate_display', 'active_users', 'average_response_time'
    ]
    list_filter = ['date']
    readonly_fields = [
        'success_rate_display', 'popular_styles_display',
        'error_distribution_display'
    ]
    
    fieldsets = (
        ('Основные метрики', {
            'fields': (
                'date', 'total_requests', 'total_successful', 'total_failed',
                'success_rate_display'
            )
        }),
        ('Пользователи', {
            'fields': ('active_users', 'new_users')
        }),
        ('Производительность', {
            'fields': (
                'average_response_time', 'total_tokens_consumed', 'total_cost'
            )
        }),
        ('Аналитика', {
            'fields': (
                'popular_styles_display', 'error_distribution_display'
            ),
            'classes': ('collapse',)
        })
    )
    
    def success_rate_display(self, obj):
        if obj.total_requests > 0:
            rate = (obj.total_successful / obj.total_requests) * 100
            return f"{rate:.1f}%"
        return "0%"
    success_rate_display.short_description = "Общая успешность"
    
    def popular_styles_display(self, obj):
        if obj.popular_styles:
            items = []
            for style, count in obj.popular_styles.items():
                items.append(f"{style}: {count}")
            return ", ".join(items)
        return "-"
    popular_styles_display.short_description = "Популярные стили"
    
    def error_distribution_display(self, obj):
        if obj.error_distribution:
            items = []
            for error, count in obj.error_distribution.items():
                items.append(f"{error}: {count}")
            return ", ".join(items)
        return "-"
    error_distribution_display.short_description = "Распределение ошибок"


# Добавляем кастомные действия для админки
@admin.action(description='Пересчитать статистику для выбранных дней')
def recalculate_stats(modeladmin, request, queryset):
    # Здесь можно добавить логику пересчета статистики
    pass


# Регистрируем действия
GlobalAIStatsAdmin.actions = [recalculate_stats] 