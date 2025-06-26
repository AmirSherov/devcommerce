from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from portfolio.models import Portfolio

User = get_user_model()


class AIGenerationRequest(models.Model):
    """Модель для отслеживания всех AI запросов пользователей"""
    
    STATUS_CHOICES = [
        ('processing', 'Обработка'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
        ('timeout', 'Таймаут'),
        ('ai_error', 'Ошибка AI'),
        ('invalid_response', 'Некорректный ответ AI'),
    ]
    
    STYLE_CHOICES = [
        ('modern', 'Современный'),
        ('minimal', 'Минимализм'),
        ('creative', 'Креативный'),
        ('business', 'Бизнес'),
        ('dark', 'Темная тема'),
        ('colorful', 'Яркий'),
    ]
    
    # Основная информация
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_requests')
    prompt = models.TextField(help_text="Промпт пользователя для AI")
    title = models.CharField(max_length=200, help_text="Название проекта")
    description = models.TextField(blank=True, help_text="Описание проекта")
    style = models.CharField(max_length=50, choices=STYLE_CHOICES, default='modern')
    
    # Результат генерации
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    portfolio_created = models.ForeignKey(
        Portfolio, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Созданное портфолио (если успешно)"
    )
    
    # Технические метрики
    response_time = models.FloatField(null=True, blank=True, help_text="Время ответа в секундах")
    tokens_used = models.IntegerField(null=True, blank=True, help_text="Использовано токенов")
    api_cost = models.DecimalField(max_digits=10, decimal_places=4, null=True, blank=True, help_text="Стоимость запроса")
    
    # Ошибки
    error_message = models.TextField(blank=True, help_text="Сообщение об ошибке")
    error_code = models.CharField(max_length=50, blank=True, help_text="Код ошибки")
    
    # AI ответ (для отладки)
    ai_raw_response = models.TextField(blank=True, help_text="Сырой ответ от AI")
    
    # Даты
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True, help_text="Время начала обработки")
    completed_at = models.DateTimeField(null=True, blank=True, help_text="Время завершения")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI запрос'
        verbose_name_plural = 'AI запросы'
    
    def __str__(self):
        return f"AI запрос #{self.id} - {self.user.username} ({self.status})"
    
    @property
    def duration(self):
        """Длительность обработки запроса"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_started(self):
        """Отметить начало обработки"""
        self.started_at = timezone.now()
        self.status = 'processing'
        self.save(update_fields=['started_at', 'status'])
    
    def mark_completed(self, status='success', portfolio=None, error_message=''):
        """Отметить завершение обработки"""
        self.completed_at = timezone.now()
        self.status = status
        if portfolio:
            self.portfolio_created = portfolio
        if error_message:
            self.error_message = error_message
        
        # Вычисляем время ответа
        if self.started_at:
            self.response_time = self.duration
        
        self.save()


class AIGenerationStats(models.Model):
    """Дневная статистика AI генераций для каждого пользователя"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_stats')
    date = models.DateField(help_text="Дата статистики")
    
    # Счетчики запросов
    requests_count = models.IntegerField(default=0, help_text="Общее количество запросов")
    successful_count = models.IntegerField(default=0, help_text="Успешных генераций")
    failed_count = models.IntegerField(default=0, help_text="Неудачных генераций")
    
    # Метрики производительности
    total_response_time = models.FloatField(default=0.0, help_text="Общее время ответов")
    total_tokens_used = models.IntegerField(default=0, help_text="Общее количество токенов")
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0, help_text="Общая стоимость")
    
    # Популярные стили
    popular_styles = models.JSONField(default=dict, help_text="Статистика по стилям")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Статистика AI'
        verbose_name_plural = 'Статистика AI'
    
    def __str__(self):
        return f"AI статистика {self.user.username} - {self.date}"
    
    @property
    def success_rate(self):
        """Процент успешных генераций"""
        if self.requests_count == 0:
            return 0
        return round((self.successful_count / self.requests_count) * 100, 2)
    
    @property
    def average_response_time(self):
        """Среднее время ответа"""
        if self.successful_count == 0:
            return 0
        return round(self.total_response_time / self.successful_count, 2)


class AIPromptTemplate(models.Model):
    """Шаблоны промптов для повторного использования"""
    
    CATEGORY_CHOICES = [
        ('landing', 'Лендинг'),
        ('portfolio', 'Портфолио'),
        ('blog', 'Блог'),
        ('ecommerce', 'Магазин'),
        ('corporate', 'Корпоративный'),
        ('creative', 'Креативный'),
        ('other', 'Другое'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_templates')
    name = models.CharField(max_length=100, help_text="Название шаблона")
    prompt = models.TextField(help_text="Текст промпта")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    style = models.CharField(max_length=50, choices=AIGenerationRequest.STYLE_CHOICES, default='modern')
    
    # Статистика использования
    usage_count = models.IntegerField(default=0, help_text="Количество использований")
    success_rate = models.FloatField(default=0.0, help_text="Процент успешных генераций")
    
    is_public = models.BooleanField(default=False, help_text="Доступен другим пользователям")
    is_featured = models.BooleanField(default=False, help_text="Рекомендуемый шаблон")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', '-created_at']
        verbose_name = 'Шаблон промпта'
        verbose_name_plural = 'Шаблоны промптов'
    
    def __str__(self):
        return f"Шаблон: {self.name} ({self.user.username})"
    
    def increment_usage(self):
        """Увеличить счетчик использования"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class GlobalAIStats(models.Model):
    """Глобальная статистика AI генераций"""
    
    date = models.DateField(unique=True, help_text="Дата статистики")
    
    # Общие метрики
    total_requests = models.IntegerField(default=0)
    total_successful = models.IntegerField(default=0)
    total_failed = models.IntegerField(default=0)
    
    # Пользователи
    active_users = models.IntegerField(default=0, help_text="Активных пользователей")
    new_users = models.IntegerField(default=0, help_text="Новых пользователей AI")
    
    # Производительность
    average_response_time = models.FloatField(default=0.0)
    total_tokens_consumed = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    
    # Популярные данные
    popular_styles = models.JSONField(default=dict)
    popular_prompts = models.JSONField(default=list)
    error_distribution = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Глобальная AI статистика'
        verbose_name_plural = 'Глобальная AI статистика'
    
    def __str__(self):
        return f"Глобальная AI статистика - {self.date}" 