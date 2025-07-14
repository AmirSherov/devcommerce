from rest_framework import serializers
from .models import PublicAPIKey, PublicAPIRequest, PublicAPIUsage, PublicAPILimit
from storage.models import StorageFile


class PublicAPIKeySerializer(serializers.ModelSerializer):
    """Сериализатор для API ключей"""
    
    container_name = serializers.ReadOnlyField(source='container.name')
    user_plan = serializers.ReadOnlyField(source='container.user.plan')
    
    class Meta:
        model = PublicAPIKey
        fields = [
            'id', 'api_key', 'is_active', 'permissions',
            'rate_limit_per_hour', 'max_file_size_mb',
            'total_requests', 'last_used_at',
            'container_name', 'user_plan',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'api_key', 'total_requests', 'last_used_at',
            'container_name', 'user_plan', 'created_at', 'updated_at'
        ]


class PublicAPIKeyCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания API ключей"""
    
    class Meta:
        model = PublicAPIKey
        fields = ['permissions', 'rate_limit_per_hour', 'max_file_size_mb']


class PublicAPIRequestSerializer(serializers.ModelSerializer):
    """Сериализатор для запросов API"""
    
    container_name = serializers.ReadOnlyField(source='api_key.container.name')
    
    class Meta:
        model = PublicAPIRequest
        fields = [
            'id', 'method', 'endpoint', 'status_code',
            'user_agent', 'ip_address', 'request_size', 'response_size',
            'response_time', 'error_message', 'error_code',
            'container_name', 'created_at'
        ]
        read_only_fields = [
            'id', 'method', 'endpoint', 'status_code',
            'user_agent', 'ip_address', 'request_size', 'response_size',
            'response_time', 'error_message', 'error_code',
            'container_name', 'created_at'
        ]


class PublicAPIUsageSerializer(serializers.ModelSerializer):
    """Сериализатор для статистики API"""
    
    container_name = serializers.ReadOnlyField(source='api_key.container.name')
    success_rate = serializers.ReadOnlyField()
    
    class Meta:
        model = PublicAPIUsage
        fields = [
            'date', 'total_requests', 'successful_requests', 'failed_requests',
            'files_uploaded', 'files_downloaded', 'total_upload_size', 'total_download_size',
            'total_response_time', 'average_response_time', 'popular_endpoints',
            'container_name', 'success_rate', 'created_at'
        ]


class PublicAPILimitSerializer(serializers.ModelSerializer):
    """Сериализатор для лимитов API"""
    
    class Meta:
        model = PublicAPILimit
        fields = [
            'plan', 'requests_per_hour', 'requests_per_day',
            'max_file_size_mb', 'max_files_per_request', 'storage_limit_mb',
            'api_access', 'custom_domains', 'advanced_analytics'
        ]


class PublicFileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов через API"""
    
    file = serializers.FileField(help_text="Файл для загрузки")
    filename = serializers.CharField(max_length=255, required=False, help_text="Кастомное имя файла")
    is_public = serializers.BooleanField(default=False, help_text="Сделать файл публичным")
    metadata = serializers.JSONField(required=False, help_text="Дополнительные метаданные")


class PublicFileListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка файлов через API"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = StorageFile
        fields = [
            'id', 'filename', 'file_size_mb', 'mime_type', 'is_public',
            'is_image', 'is_video', 'is_document', 'download_url', 'created_at'
        ]
    
    def get_download_url(self, obj):
        """Генерирует URL для скачивания файла"""
        if obj.is_public:
            return f"/api/public/storage/files/{obj.id}/download/"
        return None


class PublicFileDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о файле"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    download_url = serializers.SerializerMethodField()
    
    class Meta:
        model = StorageFile
        fields = [
            'id', 'filename', 'original_filename', 'file_size_mb',
            'mime_type', 'file_extension', 'is_public',
            'is_image', 'is_video', 'is_document', 'download_url',
            'created_at', 'updated_at'
        ]
    
    def get_download_url(self, obj):
        """Генерирует URL для скачивания файла"""
        if obj.is_public:
            return f"/api/public/storage/files/{obj.id}/download/"
        return None


class PublicAPIStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики API"""
    
    # Общая статистика
    total_requests = serializers.IntegerField(help_text="Общее количество запросов")
    successful_requests = serializers.IntegerField(help_text="Успешных запросов")
    failed_requests = serializers.IntegerField(help_text="Неудачных запросов")
    success_rate = serializers.FloatField(help_text="Процент успешных запросов")
    
    # Статистика файлов
    total_files = serializers.IntegerField(help_text="Общее количество файлов")
    files_uploaded = serializers.IntegerField(help_text="Загружено файлов")
    files_downloaded = serializers.IntegerField(help_text="Скачано файлов")
    total_upload_size_mb = serializers.FloatField(help_text="Общий размер загрузок в MB")
    total_download_size_mb = serializers.FloatField(help_text="Общий размер скачиваний в MB")
    
    # Производительность
    average_response_time = serializers.FloatField(help_text="Среднее время ответа")
    total_response_time = serializers.FloatField(help_text="Общее время ответов")
    
    # Популярные эндпоинты
    popular_endpoints = serializers.ListField(help_text="Популярные эндпоинты")
    
    # Лимиты
    rate_limit_per_hour = serializers.IntegerField(help_text="Лимит запросов в час")
    requests_remaining = serializers.IntegerField(help_text="Осталось запросов в час")
    max_file_size_mb = serializers.IntegerField(help_text="Максимальный размер файла в MB") 