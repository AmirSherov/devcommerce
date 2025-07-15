from django.contrib import admin
from .models import PublicAPIKey, PublicAPIRequest, PublicAPIUsage, PublicAPILimit


@admin.register(PublicAPIKey)
class PublicAPIKeyAdmin(admin.ModelAdmin):
    list_display = ['container', 'api_key', 'is_active', 'total_requests', 'last_used_at', 'created_at']
    list_filter = ['is_active', 'created_at', 'container__user__plan']
    search_fields = ['container__name', 'api_key', 'container__user__email']
    readonly_fields = ['id', 'api_key', 'api_secret', 'total_requests', 'last_used_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'container')
        }),
        ('API ключи', {
            'fields': ('api_key', 'api_secret')
        }),
        ('Настройки доступа', {
            'fields': ('is_active', 'permissions')
        }),
        ('Лимиты', {
            'fields': ('rate_limit_per_hour', 'max_file_size_mb')
        }),
        ('Статистика', {
            'fields': ('total_requests', 'last_used_at')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PublicAPIRequest)
class PublicAPIRequestAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'method', 'endpoint', 'status_code', 'response_time', 'created_at']
    list_filter = ['method', 'status_code', 'created_at', 'api_key__container']
    search_fields = ['api_key__api_key', 'endpoint', 'error_message']
    readonly_fields = ['id', 'created_at']
    
    fieldsets = (
        ('Запрос', {
            'fields': ('id', 'api_key', 'method', 'endpoint', 'status_code')
        }),
        ('Метаданные', {
            'fields': ('user_agent', 'ip_address', 'request_size', 'response_size')
        }),
        ('Производительность', {
            'fields': ('response_time',)
        }),
        ('Ошибки', {
            'fields': ('error_message', 'error_code')
        }),
        ('Файлы', {
            'fields': ('file_uploaded',)
        }),
        ('Временные метки', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Запросы создаются автоматически


@admin.register(PublicAPIUsage)
class PublicAPIUsageAdmin(admin.ModelAdmin):
    list_display = ['api_key', 'date', 'total_requests', 'success_rate', 'files_uploaded', 'files_downloaded']
    list_filter = ['date', 'api_key__container']
    search_fields = ['api_key__container__name', 'api_key__api_key']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('api_key', 'date')
        }),
        ('Метрики запросов', {
            'fields': ('total_requests', 'successful_requests', 'failed_requests')
        }),
        ('Метрики файлов', {
            'fields': ('files_uploaded', 'files_downloaded', 'total_upload_size', 'total_download_size')
        }),
        ('Производительность', {
            'fields': ('total_response_time', 'average_response_time')
        }),
        ('Статистика эндпоинтов', {
            'fields': ('popular_endpoints',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(PublicAPILimit)
class PublicAPILimitAdmin(admin.ModelAdmin):
    list_display = ['plan', 'requests_per_hour', 'requests_per_day', 'max_file_size_mb', 'api_access']
    list_filter = ['api_access', 'custom_domains', 'advanced_analytics']
    search_fields = ['plan']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_fieldsets(self, request, obj=None):
        if obj and obj.plan == 'pro':
            # Для Pro плана скрываем лимит хранилища
            return (
                ('План', {
                    'fields': ('plan',)
                }),
                ('Лимиты запросов', {
                    'fields': ('requests_per_hour', 'requests_per_day')
                }),
                ('Лимиты файлов', {
                    'fields': ('max_file_size_mb', 'max_files_per_request')
                }),
                ('Дополнительные возможности', {
                    'fields': ('api_access', 'custom_domains', 'advanced_analytics')
                }),
                ('Временные метки', {
                    'fields': ('created_at', 'updated_at')
                }),
            )
        else:
            # Для других планов показываем лимит хранилища
            return (
                ('План', {
                    'fields': ('plan',)
                }),
                ('Лимиты запросов', {
                    'fields': ('requests_per_hour', 'requests_per_day')
                }),
                ('Лимиты файлов', {
                    'fields': ('max_file_size_mb', 'max_files_per_request')
                }),
                ('Лимиты хранилища', {
                    'fields': ('storage_limit_mb',)
                }),
                ('Дополнительные возможности', {
                    'fields': ('api_access', 'custom_domains', 'advanced_analytics')
                }),
                ('Временные метки', {
                    'fields': ('created_at', 'updated_at')
                }),
            )
    
    def save_model(self, request, obj, form, change):
        # Для Pro плана автоматически устанавливаем storage_limit_mb в None
        if obj.plan == 'pro':
            obj.storage_limit_mb = None
        super().save_model(request, obj, form, change)
