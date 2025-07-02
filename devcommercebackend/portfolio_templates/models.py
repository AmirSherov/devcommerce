from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinLengthValidator

User = get_user_model()


class PortfolioTemplate(models.Model):
    """
    🎨 МОДЕЛЬ ШАБЛОНА ПОРТФОЛИО
    
    Система готовых шаблонов для быстрого создания портфолио
    """
    
    CATEGORY_CHOICES = [
        ('fullstack', 'Fullstack Developer'),
        ('frontend', 'Frontend Developer'),
        ('backend', 'Backend Developer'),
        ('mobile', 'Mobile Developer'),
        ('devops', 'DevOps Engineer'),
        ('data_scientist', 'Data Scientist'),
        ('ml_engineer', 'ML Engineer'),
        ('qa_engineer', 'QA Engineer'),
        ('ui_designer', 'UI/UX Designer'),
        ('product_manager', 'Product Manager'),
        ('cyber_security', 'Cybersecurity Specialist'),
        ('blockchain', 'Blockchain Developer'),
        ('game_developer', 'Game Developer'),
        ('ai_engineer', 'AI Engineer'),
        ('cloud_architect', 'Cloud Architect'),
        ('business_analyst', 'Business Analyst'),
        ('scrum_master', 'Scrum Master'),
        ('technical_writer', 'Technical Writer'),
        ('sales_engineer', 'Sales Engineer'),
        ('other', 'Другая специализация'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Начинающий'),
        ('intermediate', 'Средний'),
        ('advanced', 'Продвинутый'),
    ]
    
    # Основная информация
    title = models.CharField(
        max_length=200, 
        help_text="Название шаблона",
        validators=[MinLengthValidator(3)]
    )
    
    description = models.TextField(
        help_text="Описание шаблона и его особенностей",
        validators=[MinLengthValidator(10)]
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default='fullstack',
        help_text="IT специализация для которой предназначен шаблон"
    )
    
    difficulty = models.CharField(
        max_length=20,
        choices=DIFFICULTY_CHOICES,
        default='intermediate',
        help_text="Уровень сложности шаблона"
    )
    
    # Код шаблона
    html_code = models.TextField(
        help_text="HTML код шаблона",
        validators=[MinLengthValidator(50)]
    )
    
    css_code = models.TextField(
        help_text="CSS код шаблона",
        validators=[MinLengthValidator(50)]
    )
    
    js_code = models.TextField(
        blank=True,
        help_text="JavaScript код шаблона (необязательно)"
    )
    
    # Превью и метаданные
    thumbnail_image = models.URLField(
        blank=True,
        help_text="URL превью изображения шаблона"
    )
    
    demo_url = models.URLField(
        blank=True,
        help_text="Ссылка на демо шаблона (необязательно)"
    )
    
    tags = models.JSONField(
        default=list,
        help_text="Теги для поиска (список строк)"
    )
    
    # Статистика
    likes = models.PositiveIntegerField(
        default=0,
        help_text="Количество лайков"
    )
    
    views = models.PositiveIntegerField(
        default=0,
        help_text="Количество просмотров"
    )
    
    uses = models.PositiveIntegerField(
        default=0,
        help_text="Количество использований"
    )
    
    # Управление
    is_active = models.BooleanField(
        default=True,
        help_text="Активен ли шаблон"
    )
    
    is_featured = models.BooleanField(
        default=False,
        help_text="Рекомендуемый шаблон"
    )
    
    is_premium = models.BooleanField(
        default=False,
        help_text="Премиум шаблон"
    )
    
    # Автор и временные метки
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_templates',
        help_text="Создатель шаблона"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_featured', '-likes', '-created_at']
        verbose_name = 'Шаблон портфолио'
        verbose_name_plural = 'Шаблоны портфолио'
        indexes = [
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['is_featured', 'is_active']),
            models.Index(fields=['-likes', '-views']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"
    
    def increment_views(self):
        """Увеличить счетчик просмотров"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def increment_uses(self):
        """Увеличить счетчик использований"""
        self.uses += 1
        self.save(update_fields=['uses'])
    
    def add_like(self):
        """Добавить лайк"""
        self.likes += 1
        self.save(update_fields=['likes'])
    
    def remove_like(self):
        """Убрать лайк"""
        if self.likes > 0:
            self.likes -= 1
            self.save(update_fields=['likes'])
    
    @property
    def preview_html(self):
        """Получить HTML для превью"""
        return self.html_code[:500] + '...' if len(self.html_code) > 500 else self.html_code
    
    @property
    def is_popular(self):
        """Популярный ли шаблон"""
        return self.likes >= 10 or self.uses >= 50


class TemplateUsage(models.Model):
    """
    📊 МОДЕЛЬ ИСПОЛЬЗОВАНИЯ ШАБЛОНА
    
    Отслеживание кто и когда использовал шаблон
    """
    
    template = models.ForeignKey(
        PortfolioTemplate,
        on_delete=models.CASCADE,
        related_name='usages'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='template_usages'
    )
    
    portfolio_created = models.ForeignKey(
        'portfolio.Portfolio',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="Созданное портфолио на основе шаблона"
    )
    
    used_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['template', 'user', 'portfolio_created']
        ordering = ['-used_at']
        verbose_name = 'Использование шаблона'
        verbose_name_plural = 'Использования шаблонов'
    
    def __str__(self):
        return f"{self.user.username} использовал {self.template.title}"


class TemplateLike(models.Model):
    """
    👍 МОДЕЛЬ ЛАЙКОВ ШАБЛОНОВ
    """
    
    template = models.ForeignKey(
        PortfolioTemplate,
        on_delete=models.CASCADE,
        related_name='template_likes'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='liked_templates'
    )
    
    liked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['template', 'user']
        ordering = ['-liked_at']
        verbose_name = 'Лайк шаблона'
        verbose_name_plural = 'Лайки шаблонов'
    
    def __str__(self):
        return f"{self.user.username} лайкнул {self.template.title}"
