import uuid
from django.db import models
from django.conf import settings
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


def validate_https_url(value):
    """Валидатор для проверки что URL начинается с https://"""
    if value and not value.startswith('https://'):
        raise ValidationError(_('URL должен начинаться с https://'))


class Project(models.Model):
    STATUS_CHOICES = [
        ('public', 'Публичный'),
        ('profile_only', 'Виден только в профиле'),
        ('private', 'Закрытый'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Название проекта")
    description = models.TextField(verbose_name="Описание проекта")
    github_link = models.URLField(
        blank=True, 
        null=True, 
        verbose_name="Ссылка на GitHub"
    )
    project_public_link = models.URLField(
        validators=[validate_https_url],
        verbose_name="Публичная ссылка на проект"
    )
    project_photo = models.ImageField(
        upload_to='projects/photos/', 
        blank=True, 
        null=True,
        verbose_name="Изображение проекта"
    )
    status = models.CharField(
        max_length=20, 
        choices=STATUS_CHOICES, 
        default='public',
        verbose_name="Статус проекта"
    )
    technologies = models.JSONField(
        default=list,
        verbose_name="Технологии",
        help_text="Список технологий в формате JSON"
    )
    likes = models.PositiveIntegerField(default=0, verbose_name="Количество лайков")
    views = models.PositiveIntegerField(default=0, verbose_name="Количество просмотров")
    comments_count = models.PositiveIntegerField(default=0, verbose_name="Количество комментариев")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name="Автор"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
        verbose_name="URL-путь"
    )

    class Meta:
        verbose_name = "Проект"
        verbose_name_plural = "Проекты"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['author', 'status']),
            models.Index(fields=['slug']),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self.generate_unique_slug()
        super().save(*args, **kwargs)

    def generate_unique_slug(self):
        """Генерирует уникальный slug на основе заголовка"""
        base_slug = slugify(self.title)
        if not base_slug:
            base_slug = f"project-{uuid.uuid4().hex[:8]}"
        
        slug = base_slug
        counter = 1
        while Project.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def increment_views(self):
        """Увеличивает счетчик просмотров"""
        self.views += 1
        self.save(update_fields=['views'])

    def increment_likes(self):
        """Увеличивает счетчик лайков"""
        self.likes += 1
        self.save(update_fields=['likes'])

    def decrement_likes(self):
        """Уменьшает счетчик лайков"""
        if self.likes > 0:
            self.likes -= 1
            self.save(update_fields=['likes'])

    def is_visible_to_user(self, user):
        """Проверяет, виден ли проект пользователю"""
        if self.status == 'public':
            return True
        elif self.status == 'profile_only':
            # Виден всем в профиле автора
            return True
        elif self.status == 'private':
            # Виден только автору
            return user == self.author
        return False

    def __str__(self):
        return self.title
