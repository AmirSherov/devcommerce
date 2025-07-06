from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from portfolio.models import Portfolio
from portfolio_templates.models import PortfolioTemplate

User = get_user_model()


class TemplateAIGeneration(models.Model):
    """
    🤖 МОДЕЛЬ ДЛЯ AI ЗАПОЛНЕНИЯ ШАБЛОНОВ
    
    Отслеживает каждый случай использования AI для персонализации шаблонов
    """
    
    STATUS_CHOICES = [
        ('processing', 'Обработка'),
        ('success', 'Успешно'),
        ('failed', 'Ошибка'),
        ('ai_error', 'Ошибка AI'),
        ('invalid_html', 'Некорректный HTML'),
        ('server_overload', 'Перегрузка сервера'),
    ]
    
    # Основная информация
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_ai_generations')
    template = models.ForeignKey(PortfolioTemplate, on_delete=models.CASCADE, related_name='ai_generations')
    
    # Данные запроса
    project_title = models.CharField(max_length=200, help_text="Название проекта")
    project_description = models.TextField(help_text="Описание проекта")
    user_data = models.TextField(help_text="Данные пользователя для AI")
    
    # Результат
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='processing')
    portfolio_created = models.ForeignKey(
        Portfolio, 
        null=True, 
        blank=True, 
        on_delete=models.SET_NULL,
        help_text="Созданное портфолио"
    )
    
    # Технические метрики
    response_time = models.FloatField(null=True, blank=True, help_text="Время ответа AI в секундах")
    tokens_used = models.IntegerField(null=True, blank=True, help_text="Использовано токенов")
    
    # Отладка и ошибки
    error_message = models.TextField(blank=True, help_text="Сообщение об ошибке")
    ai_raw_response = models.TextField(blank=True, help_text="Сырой ответ от AI")
    original_html = models.TextField(blank=True, help_text="Оригинальный HTML шаблона")
    generated_html = models.TextField(blank=True, help_text="HTML после AI обработки")
    
    # Временные метки
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'AI генерация шаблона'
        verbose_name_plural = 'AI генерации шаблонов'
    
    def __str__(self):
        return f"AI генерация #{self.id} - {self.user.username} ({self.template.title})"
    
    @property
    def duration(self):
        """Длительность обработки"""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None
    
    def mark_started(self):
        """Отметить начало обработки"""
        self.started_at = timezone.now()
        self.status = 'processing'
        self.save(update_fields=['started_at', 'status'])
    
    def mark_completed(self, status='success', portfolio=None, error_message='', generated_html=''):
        """Отметить завершение обработки"""
        self.completed_at = timezone.now()
        self.status = status
        if portfolio:
            self.portfolio_created = portfolio
        if error_message:
            self.error_message = error_message
        if generated_html:
            self.generated_html = generated_html
        
        # Вычисляем время ответа
        if self.started_at:
            self.response_time = self.duration
        
        self.save()


class TemplateAIStats(models.Model):
    """
    📊 СТАТИСТИКА AI ГЕНЕРАЦИЙ ПО ШАБЛОНАМ
    
    Ежедневная статистика использования AI для каждого пользователя
    """
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='template_ai_stats')
    date = models.DateField(help_text="Дата статистики")
    
    # Счетчики AI генераций
    ai_requests_count = models.IntegerField(default=0, help_text="Количество AI запросов")
    ai_successful_count = models.IntegerField(default=0, help_text="Успешных AI генераций")
    ai_failed_count = models.IntegerField(default=0, help_text="Неудачных AI генераций")
    
    # Счетчики обычного использования шаблонов
    regular_usage_count = models.IntegerField(default=0, help_text="Обычное использование шаблонов")
    
    # Метрики производительности
    total_ai_response_time = models.FloatField(default=0.0, help_text="Общее время AI ответов")
    total_tokens_used = models.IntegerField(default=0, help_text="Общее количество токенов")
    
    # Популярные шаблоны
    popular_templates = models.JSONField(default=dict, help_text="Статистика по шаблонам")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
        verbose_name = 'Статистика AI шаблонов'
        verbose_name_plural = 'Статистика AI шаблонов'
    
    def __str__(self):
        return f"AI статистика {self.user.username} - {self.date}"
    
    @property
    def ai_success_rate(self):
        """Процент успешных AI генераций"""
        if self.ai_requests_count == 0:
            return 0
        return round((self.ai_successful_count / self.ai_requests_count) * 100, 2)
    
    @property
    def total_usage(self):
        """Общее использование (AI + обычное)"""
        return self.ai_requests_count + self.regular_usage_count


class GlobalTemplateAIStats(models.Model):
    """
    🌍 ГЛОБАЛЬНАЯ СТАТИСТИКА AI ГЕНЕРАЦИЙ ШАБЛОНОВ
    """
    
    date = models.DateField(unique=True, help_text="Дата статистики")
    
    # AI метрики
    total_ai_requests = models.IntegerField(default=0)
    total_ai_successful = models.IntegerField(default=0)
    total_ai_failed = models.IntegerField(default=0)
    
    # Обычное использование
    total_regular_usage = models.IntegerField(default=0)
    
    # Пользователи
    active_ai_users = models.IntegerField(default=0, help_text="Пользователей использовавших AI")
    premium_users_count = models.IntegerField(default=0, help_text="Всего премиум пользователей")
    
    # Производительность
    average_ai_response_time = models.FloatField(default=0.0)
    total_tokens_consumed = models.IntegerField(default=0)
    
    # Популярные данные
    popular_templates_ai = models.JSONField(default=dict, help_text="Популярные шаблоны для AI")
    popular_templates_regular = models.JSONField(default=dict, help_text="Популярные шаблоны обычно")
    error_distribution = models.JSONField(default=dict, help_text="Распределение ошибок")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Глобальная статистика AI шаблонов'
        verbose_name_plural = 'Глобальная статистика AI шаблонов'
    
    def __str__(self):
        return f"Глобальная статистика AI шаблонов - {self.date}"
    
    @property
    def ai_vs_regular_ratio(self):
        """Соотношение AI к обычному использованию"""
        total = self.total_ai_requests + self.total_regular_usage
        if total == 0:
            return {"ai": 0, "regular": 0}
        return {
            "ai": round((self.total_ai_requests / total) * 100, 1),
            "regular": round((self.total_regular_usage / total) * 100, 1)
        } 