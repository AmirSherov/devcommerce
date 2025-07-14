from rest_framework import serializers
from .models import StorageContainer, StorageFile, UserStorageUsage, StorageAPILog
from .s3_utils import get_file_url_from_s3


class StorageContainerSerializer(serializers.ModelSerializer):
    """Сериализатор для контейнеров хранилища"""
    
    total_size_mb = serializers.ReadOnlyField()
    total_size_gb = serializers.ReadOnlyField()
    files_count = serializers.ReadOnlyField()
    
    class Meta:
        model = StorageContainer
        fields = [
            'id', 'name', 'api_key', 'is_public', 'is_active',
            'files_count', 'total_size', 'total_size_mb', 'total_size_gb', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'api_key', 'files_count', 'total_size', 'total_size_mb', 'total_size_gb', 'created_at', 'updated_at']


class StorageContainerCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания контейнеров"""
    
    class Meta:
        model = StorageContainer
        fields = ['name', 'is_public']


class StorageFileSerializer(serializers.ModelSerializer):
    """Сериализатор для файлов хранилища"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    container_name = serializers.ReadOnlyField(source='container.name')
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        return get_file_url_from_s3(obj.s3_key)
    
    class Meta:
        model = StorageFile
        fields = [
            'id', 'filename', 'original_filename', 'file_size', 'file_size_mb',
            'mime_type', 'file_extension', 'is_public', 'is_active',
            'is_image', 'is_video', 'is_document', 'container_name', 'file_url',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'filename', 'file_size', 'file_size_mb', 'mime_type', 'file_extension',
            'is_image', 'is_video', 'is_document', 'container_name', 'file_url', 'created_at', 'updated_at'
        ]


class StorageFileUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки файлов"""
    
    file = serializers.FileField(help_text="Файл для загрузки")
    filename = serializers.CharField(max_length=255, required=False, help_text="Кастомное имя файла")
    is_public = serializers.BooleanField(default=False, help_text="Сделать файл публичным")


class StorageFileListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка файлов"""
    
    file_size_mb = serializers.ReadOnlyField()
    is_image = serializers.ReadOnlyField()
    is_video = serializers.ReadOnlyField()
    is_document = serializers.ReadOnlyField()
    file_url = serializers.SerializerMethodField()

    def get_file_url(self, obj):
        return get_file_url_from_s3(obj.s3_key)
    
    class Meta:
        model = StorageFile
        fields = [
            'id', 'filename', 'file_size', 'file_size_mb', 'mime_type', 'is_public',
            'is_image', 'is_video', 'is_document', 'file_url', 'created_at'
        ]


class UserStorageUsageSerializer(serializers.ModelSerializer):
    """Сериализатор для статистики использования хранилища"""
    
    usage_mb = serializers.ReadOnlyField()
    usage_gb = serializers.ReadOnlyField()
    
    class Meta:
        model = UserStorageUsage
        fields = [
            'date', 'bytes_used', 'usage_mb', 'usage_gb', 'files_count', 'containers_count',
            'uploads_count', 'uploads_size', 'deletions_count', 'deletions_size',
            'file_types_stats', 'created_at'
        ]


class StorageAPILogSerializer(serializers.ModelSerializer):
    """Сериализатор для логов API"""
    
    container_name = serializers.ReadOnlyField(source='container.name')
    
    class Meta:
        model = StorageAPILog
        fields = [
            'container', 'container_name', 'api_key', 'method', 'endpoint',
            'status_code', 'response_time', 'error_message', 'user_agent',
            'ip_address', 'created_at'
        ]
        read_only_fields = [
            'container', 'container_name', 'api_key', 'method', 'endpoint',
            'status_code', 'response_time', 'error_message', 'user_agent',
            'ip_address', 'created_at'
        ]


class StorageLimitsSerializer(serializers.Serializer):
    """Сериализатор для лимитов хранилища"""
    
    plan = serializers.CharField(help_text="Текущий план пользователя")
    storage_limit_mb = serializers.IntegerField(help_text="Лимит хранилища в MB")
    storage_limit_gb = serializers.FloatField(help_text="Лимит хранилища в GB")
    storage_used_mb = serializers.FloatField(help_text="Использовано MB")
    storage_used_gb = serializers.FloatField(help_text="Использовано GB")
    storage_remaining_mb = serializers.FloatField(help_text="Осталось MB")
    storage_remaining_gb = serializers.FloatField(help_text="Осталось GB")
    usage_percentage = serializers.FloatField(help_text="Процент использования")
    can_upload = serializers.BooleanField(help_text="Можно ли загружать файлы")
    api_access = serializers.BooleanField(help_text="Доступ к API")


class StorageStatsSerializer(serializers.Serializer):
    """Сериализатор для статистики хранилища"""
    
    total_containers = serializers.IntegerField(help_text="Общее количество контейнеров")
    total_files = serializers.IntegerField(help_text="Общее количество файлов")
    total_size_mb = serializers.FloatField(help_text="Общий размер в MB")
    total_size_gb = serializers.FloatField(help_text="Общий размер в GB")
    
    # Статистика по типам файлов
    images_count = serializers.IntegerField(help_text="Количество изображений")
    videos_count = serializers.IntegerField(help_text="Количество видео")
    documents_count = serializers.IntegerField(help_text="Количество документов")
    other_files_count = serializers.IntegerField(help_text="Количество других файлов")
    
    # Популярные типы файлов
    popular_file_types = serializers.ListField(help_text="Популярные типы файлов")
    
    # Статистика загрузок
    uploads_today = serializers.IntegerField(help_text="Загрузок сегодня")
    uploads_this_week = serializers.IntegerField(help_text="Загрузок за неделю")
    uploads_this_month = serializers.IntegerField(help_text="Загрузок за месяц") 