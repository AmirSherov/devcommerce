from django.contrib import admin
from django.utils.html import format_html
from .models import StorageContainer, StorageFile, UserStorageUsage, StorageAPILog


@admin.register(StorageContainer)
class StorageContainerAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'files_count', 'total_size_mb', 'is_public', 'is_active', 'created_at']
    list_filter = ['is_public', 'is_active', 'created_at']
    search_fields = ['name', 'user__email', 'user__username']
    readonly_fields = ['id', 'api_key', 'files_count', 'total_size', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'user', 'name')
        }),
        ('API доступ', {
            'fields': ('api_key',)
        }),
        ('Настройки доступа', {
            'fields': ('is_public', 'is_active')
        }),
        ('Статистика', {
            'fields': ('files_count', 'total_size')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def total_size_mb(self, obj):
        return f"{obj.total_size_mb} MB"
    total_size_mb.short_description = 'Размер'


@admin.register(StorageFile)
class StorageFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'container', 'file_size_mb', 'mime_type', 'is_public', 'is_active', 'created_at']
    list_filter = ['mime_type', 'is_public', 'is_active', 'created_at', 'container']
    search_fields = ['filename', 'container__name', 'container__user__email']
    readonly_fields = ['id', 'file_size', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'container', 'filename', 'original_filename')
        }),
        ('Файл', {
            'fields': ('s3_key', 'file_size', 'mime_type', 'file_extension')
        }),
        ('Настройки доступа', {
            'fields': ('is_public', 'is_active')
        }),
        ('Техническая информация', {
            'fields': ('upload_session', 'checksum')
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = 'Размер'


@admin.register(UserStorageUsage)
class UserStorageUsageAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'usage_mb', 'files_count', 'containers_count', 'uploads_count']
    list_filter = ['date', 'user']
    search_fields = ['user__email', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('user', 'date')
        }),
        ('Использование', {
            'fields': ('bytes_used', 'files_count', 'containers_count')
        }),
        ('Загрузки', {
            'fields': ('uploads_count', 'uploads_size')
        }),
        ('Удаления', {
            'fields': ('deletions_count', 'deletions_size')
        }),
        ('Статистика типов файлов', {
            'fields': ('file_types_stats',)
        }),
        ('Временные метки', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def usage_mb(self, obj):
        return f"{obj.usage_mb} MB"
    usage_mb.short_description = 'Использовано'


@admin.register(StorageAPILog)
class StorageAPILogAdmin(admin.ModelAdmin):
    list_display = ['container', 'method', 'endpoint', 'status_code', 'response_time', 'created_at']
    list_filter = ['method', 'status_code', 'created_at', 'container']
    search_fields = ['container__name', 'endpoint', 'api_key']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Запрос', {
            'fields': ('container', 'api_key', 'method', 'endpoint')
        }),
        ('Ответ', {
            'fields': ('status_code', 'response_time', 'error_message')
        }),
        ('Метаданные', {
            'fields': ('user_agent', 'ip_address')
        }),
        ('Временные метки', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        return False  # Логи создаются автоматически
