import uuid
import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class StorageContainer(models.Model):
    """
    📦 МОДЕЛЬ ДЛЯ КОНТЕЙНЕРОВ ХРАНИЛИЩА
    
    Каждый пользователь может создавать контейнеры для хранения файлов
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_containers')
    name = models.CharField(max_length=100, help_text="Название контейнера")
    api_key = models.CharField(max_length=64, unique=True, help_text="Уникальный API ключ для доступа к контейнеру")
    is_public = models.BooleanField(default=False, help_text="Публичный ли доступ к контейнеру")
    is_active = models.BooleanField(default=True, help_text="Активен ли контейнер")
    files_count = models.IntegerField(default=0, help_text="Количество файлов в контейнере")
    total_size = models.BigIntegerField(default=0, help_text="Общий размер файлов в байтах")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Контейнер хранилища'
        verbose_name_plural = 'Контейнеры хранилища'
        unique_together = ['user', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.user.username})"
    
    def save(self, *args, **kwargs):
        # Генерируем API ключ при создании
        if not self.api_key:
            self.api_key = self.generate_api_key()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_api_key():
        """Генерация уникального API ключа"""
        return uuid.uuid4().hex
    
    @property
    def total_size_mb(self):
        """Размер в мегабайтах"""
        return round(self.total_size / (1024 * 1024), 2)
    
    @property
    def total_size_gb(self):
        """Размер в гигабайтах"""
        return round(self.total_size / (1024 * 1024 * 1024), 2)


class StorageFile(models.Model):
    """
    📁 МОДЕЛЬ ДЛЯ ФАЙЛОВ В ХРАНИЛИЩЕ
    
    Файлы, загруженные пользователями в контейнеры
    """
    
    # Основная информация
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    container = models.ForeignKey(StorageContainer, on_delete=models.CASCADE, related_name='files')
    
    # Информация о файле
    filename = models.CharField(max_length=255, help_text="Оригинальное имя файла")
    s3_key = models.CharField(max_length=500, help_text="Путь к файлу в S3")
    file_url = models.URLField(max_length=1000, blank=True, null=True, help_text="URL для доступа к файлу")
    file_size = models.BigIntegerField(help_text="Размер файла в байтах")
    mime_type = models.CharField(max_length=100, help_text="MIME тип файла")
    
    # Метаданные
    original_filename = models.CharField(max_length=255, help_text="Исходное имя файла")
    file_extension = models.CharField(max_length=20, blank=True, help_text="Расширение файла")
    
    # Настройки доступа
    is_public = models.BooleanField(default=False, help_text="Публичный ли файл")
    is_active = models.BooleanField(default=True, help_text="Активен ли файл")
    
    # Техническая информация
    upload_session = models.CharField(max_length=100, blank=True, help_text="ID сессии загрузки")
    checksum = models.CharField(max_length=64, blank=True, help_text="MD5 хеш файла")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Файл хранилища'
        verbose_name_plural = 'Файлы хранилища'
        unique_together = ['container', 'filename']
    
    def __str__(self):
        return f"{self.filename} ({self.container.name})"
    
    def save(self, *args, **kwargs):
        # Определяем расширение файла
        if not self.file_extension:
            self.file_extension = os.path.splitext(self.filename)[1].lower()
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        """Размер в мегабайтах"""
        return round(self.file_size / (1024 * 1024), 2)
    
    @property
    def is_image(self):
        """Является ли файл изображением"""
        return self.mime_type.startswith('image/')
    
    @property
    def is_video(self):
        """Является ли файл видео"""
        return self.mime_type.startswith('video/')
    
    @property
    def is_document(self):
        """Является ли файл документом"""
        return self.mime_type.startswith('application/') or self.mime_type.startswith('text/')


class UserStorageUsage(models.Model):
    """
    📊 МОДЕЛЬ ДЛЯ ОТСЛЕЖИВАНИЯ ИСПОЛЬЗОВАНИЯ ХРАНИЛИЩА
    
    Ежедневная статистика использования хранилища пользователями
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='storage_usage')
    date = models.DateField(help_text="Дата статистики")
    
    # Метрики использования
    bytes_used = models.BigIntegerField(default=0, help_text="Использовано байт")
    files_count = models.IntegerField(default=0, help_text="Количество файлов")
    containers_count = models.IntegerField(default=0, help_text="Количество контейнеров")
    
    # Метрики загрузок
    uploads_count = models.IntegerField(default=0, help_text="Количество загрузок")
    uploads_size = models.BigIntegerField(default=0, help_text="Размер загруженных файлов")
    
    # Метрики удалений
    deletions_count = models.IntegerField(default=0, help_text="Количество удалений")
    deletions_size = models.BigIntegerField(default=0, help_text="Размер удаленных файлов")
    
    # Популярные типы файлов
    file_types_stats = models.JSONField(default=dict, help_text="Статистика по типам файлов")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Использование хранилища'
        verbose_name_plural = 'Использование хранилища'
    
    def __str__(self):
        return f"Использование {self.user.username} - {self.date}"
    
    @property
    def usage_mb(self):
        """Использование в мегабайтах"""
        return round(self.bytes_used / (1024 * 1024), 2)
    
    @property
    def usage_gb(self):
        """Использование в гигабайтах"""
        return round(self.bytes_used / (1024 * 1024 * 1024), 2)


class StorageAPILog(models.Model):
    """
    📝 МОДЕЛЬ ДЛЯ ЛОГИРОВАНИЯ API ЗАПРОСОВ
    
    Отслеживание использования API хранилища
    """
    
    # Информация о запросе
    container = models.ForeignKey(StorageContainer, on_delete=models.CASCADE, related_name='api_logs')
    api_key = models.CharField(max_length=64, help_text="Использованный API ключ")
    
    # Детали запроса
    method = models.CharField(max_length=10, help_text="HTTP метод")
    endpoint = models.CharField(max_length=200, help_text="Эндпоинт API")
    status_code = models.IntegerField(help_text="HTTP статус код")
    
    # Метаданные
    user_agent = models.CharField(max_length=500, blank=True, help_text="User Agent")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP адрес")
    
    # Производительность
    response_time = models.FloatField(null=True, blank=True, help_text="Время ответа в секундах")
    
    # Ошибки
    error_message = models.TextField(blank=True, help_text="Сообщение об ошибке")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'API лог хранилища'
        verbose_name_plural = 'API логи хранилища'
    
    def __str__(self):
        return f"API запрос {self.method} {self.endpoint} - {self.status_code}"
