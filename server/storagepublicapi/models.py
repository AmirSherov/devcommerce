import uuid
import time
from datetime import datetime, timedelta
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from storage.models import StorageContainer

User = get_user_model()


class PublicAPIKey(models.Model):
    """
    🔑 МОДЕЛЬ ДЛЯ API КЛЮЧЕЙ ПУБЛИЧНОГО API
    
    Каждый контейнер может иметь API ключ для публичного доступа
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    container = models.OneToOneField(StorageContainer, on_delete=models.CASCADE, related_name='public_api_key')
    api_key = models.CharField(max_length=64, unique=True, help_text="Уникальный API ключ для доступа")
    api_secret = models.CharField(max_length=128, help_text="Секретный ключ для подписи запросов")
    is_active = models.BooleanField(default=True, help_text="Активен ли API ключ")
    permissions = models.JSONField(default=dict, help_text="Разрешения API ключа")
    rate_limit_per_hour = models.IntegerField(default=1000, help_text="Лимит запросов в час")
    max_file_size_mb = models.IntegerField(default=100, help_text="Максимальный размер файла в MB")
    total_requests = models.IntegerField(default=0, help_text="Общее количество запросов")
    last_used_at = models.DateTimeField(null=True, blank=True, help_text="Последнее использование")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'API ключ публичного API'
        verbose_name_plural = 'API ключи публичного API'
    
    def __str__(self):
        return f"API ключ для {self.container.name}"
    
    def save(self, *args, **kwargs):
        # Генерируем API ключ при создании
        if not self.api_key:
            self.api_key = self.generate_api_key()
        if not self.api_secret:
            self.api_secret = self.generate_api_secret()
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_api_key():
        """Генерация уникального API ключа"""
        return f"devcommerce_{uuid.uuid4().hex[:16]}"
    
    @staticmethod
    def generate_api_secret():
        """Генерация секретного ключа"""
        return uuid.uuid4().hex
    
    def can_make_request(self):
        """Проверка возможности выполнения запроса"""
        if not self.is_active:
            return False, "API ключ неактивен"
        
        # Проверяем лимит запросов в час
        hour_ago = timezone.now() - timedelta(hours=1)
        recent_requests = PublicAPIRequest.objects.filter(
            api_key=self,
            created_at__gte=hour_ago
        ).count()
        
        if recent_requests >= self.rate_limit_per_hour:
            return False, f"Превышен лимит запросов ({self.rate_limit_per_hour}/час)"
        
        return True, "Можно выполнить запрос"
    
    def update_usage(self):
        """Обновление статистики использования"""
        self.total_requests += 1
        self.last_used_at = timezone.now()
        self.save(update_fields=['total_requests', 'last_used_at'])


class PublicAPIRequest(models.Model):
    """
    📝 МОДЕЛЬ ДЛЯ ЛОГИРОВАНИЯ ЗАПРОСОВ ПУБЛИЧНОГО API
    
    Отслеживание всех запросов к публичному API
    """
    
    # Информация о запросе
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    api_key = models.ForeignKey(PublicAPIKey, on_delete=models.CASCADE, related_name='requests')
    
    # Детали запроса
    method = models.CharField(max_length=10, help_text="HTTP метод")
    endpoint = models.CharField(max_length=200, help_text="Эндпоинт API")
    status_code = models.IntegerField(help_text="HTTP статус код")
    
    # Метаданные
    user_agent = models.CharField(max_length=500, blank=True, help_text="User Agent")
    ip_address = models.GenericIPAddressField(blank=True, null=True, help_text="IP адрес")
    request_size = models.IntegerField(default=0, help_text="Размер запроса в байтах")
    response_size = models.IntegerField(default=0, help_text="Размер ответа в байтах")
    
    # Производительность
    response_time = models.FloatField(null=True, blank=True, help_text="Время ответа в секундах")
    
    # Ошибки
    error_message = models.TextField(blank=True, help_text="Сообщение об ошибке")
    error_code = models.CharField(max_length=50, blank=True, help_text="Код ошибки")
    
    # Файлы (если применимо)
    file_uploaded = models.ForeignKey(
        'storage.StorageFile', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='public_api_requests'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Запрос публичного API'
        verbose_name_plural = 'Запросы публичного API'
    
    def __str__(self):
        return f"API запрос {self.method} {self.endpoint} - {self.status_code}"


class PublicAPIUsage(models.Model):
    """
    📊 МОДЕЛЬ ДЛЯ СТАТИСТИКИ ИСПОЛЬЗОВАНИЯ ПУБЛИЧНОГО API
    
    Ежедневная статистика использования API для каждого контейнера
    """
    
    api_key = models.ForeignKey(PublicAPIKey, on_delete=models.CASCADE, related_name='usage_stats')
    date = models.DateField(help_text="Дата статистики")
    
    # Метрики запросов
    total_requests = models.IntegerField(default=0, help_text="Общее количество запросов")
    successful_requests = models.IntegerField(default=0, help_text="Успешных запросов")
    failed_requests = models.IntegerField(default=0, help_text="Неудачных запросов")
    
    # Метрики файлов
    files_uploaded = models.IntegerField(default=0, help_text="Загружено файлов")
    files_downloaded = models.IntegerField(default=0, help_text="Скачано файлов")
    total_upload_size = models.BigIntegerField(default=0, help_text="Общий размер загрузок")
    total_download_size = models.BigIntegerField(default=0, help_text="Общий размер скачиваний")
    
    # Метрики производительности
    total_response_time = models.FloatField(default=0.0, help_text="Общее время ответов")
    average_response_time = models.FloatField(default=0.0, help_text="Среднее время ответа")
    
    # Популярные эндпоинты
    popular_endpoints = models.JSONField(default=dict, help_text="Статистика по эндпоинтам")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['api_key', 'date']
        ordering = ['-date']
        verbose_name = 'Статистика публичного API'
        verbose_name_plural = 'Статистика публичного API'
    
    def __str__(self):
        return f"API статистика {self.api_key.container.name} - {self.date}"
    
    @property
    def success_rate(self):
        """Процент успешных запросов"""
        if self.total_requests == 0:
            return 0
        return round((self.successful_requests / self.total_requests) * 100, 2)


class PublicAPILimit(models.Model):
    """
    🚫 МОДЕЛЬ ДЛЯ ОГРАНИЧЕНИЙ ПУБЛИЧНОГО API
    
    Настройки лимитов для разных планов пользователей
    """
    
    PLAN_CHOICES = [
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('pro', 'Pro'),
    ]
    
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES, unique=True)
    
    # Лимиты запросов
    requests_per_hour = models.IntegerField(help_text="Запросов в час")
    requests_per_day = models.IntegerField(help_text="Запросов в день")
    
    # Лимиты файлов
    max_file_size_mb = models.IntegerField(help_text="Максимальный размер файла в MB")
    max_files_per_request = models.IntegerField(help_text="Максимум файлов за запрос")
    
    # Лимиты хранилища
    storage_limit_mb = models.IntegerField(null=True, blank=True, help_text="Лимит хранилища в MB (null = безлимитно)")
    
    # Дополнительные возможности
    api_access = models.BooleanField(default=False, help_text="Доступ к API")
    custom_domains = models.BooleanField(default=False, help_text="Кастомные домены")
    advanced_analytics = models.BooleanField(default=False, help_text="Продвинутая аналитика")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Лимит публичного API'
        verbose_name_plural = 'Лимиты публичного API'
    
    def __str__(self):
        return f"Лимиты для плана {self.plan}"
    
    @classmethod
    def get_limits_for_plan(cls, plan):
        """Получение лимитов для плана"""
        try:
            return cls.objects.get(plan=plan)
        except cls.DoesNotExist:
            # Возвращаем стандартные лимиты если план не найден
            return cls.objects.get(plan='standard')
