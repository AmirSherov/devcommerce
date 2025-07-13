from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import uuid

User = get_user_model()


class UserProfile(models.Model):
    """Расширенная информация профиля пользователя"""
    
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
        ('other', 'Другой'),
        ('prefer_not_to_say', 'Предпочитаю не указывать'),
    ]
    
    VISIBILITY_CHOICES = [
        ('public', 'Публичный'),
        ('private', 'Приватный'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # Основная информация
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, verbose_name="О себе")
    location = models.CharField(max_length=100, blank=True, verbose_name="Локация")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, verbose_name="Пол")
    
    # Социальные ссылки
    social_links = models.JSONField(default=dict, blank=True, verbose_name="Социальные ссылки")
    
    # Настройки приватности
    profile_visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='public',
        verbose_name="Видимость профиля"
    )
    projects_visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='public',
        verbose_name="Видимость проектов"
    )
    portfolio_visibility = models.CharField(
        max_length=20, 
        choices=VISIBILITY_CHOICES, 
        default='public',
        verbose_name="Видимость портфолио"
    )
    notify_new_followers = models.BooleanField(
        default=True, 
        verbose_name="Уведомления о новых подписчиках"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"
    
    def __str__(self):
        return f"Профиль {self.user.email}"
    
    @property
    def age(self):
        """Возраст пользователя"""
        if self.birth_date:
            today = timezone.now().date()
            return today.year - self.birth_date.year - (
                (today.month, today.day) < (self.birth_date.month, self.birth_date.day)
            )
        return None


class UserNotificationSettings(models.Model):
    """Настройки уведомлений пользователя"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings')
    
    # Email уведомления
    email_notifications = models.BooleanField(default=True, verbose_name="Email уведомления")
    project_notifications = models.BooleanField(default=True, verbose_name="Уведомления о проектах")
    like_comment_notifications = models.BooleanField(default=True, verbose_name="Уведомления о лайках и комментариях")
    template_notifications = models.BooleanField(default=True, verbose_name="Уведомления о новых шаблонах")
    weekly_newsletter = models.BooleanField(default=True, verbose_name="Еженедельная рассылка")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Настройки уведомлений"
        verbose_name_plural = "Настройки уведомлений"
    
    def __str__(self):
        return f"Настройки уведомлений {self.user.email}"


class UserSession(models.Model):
    """Активные сессии пользователя"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    session_key = models.CharField(max_length=40, unique=True)
    jwt_token_hash = models.CharField(max_length=255, blank=True, null=True, verbose_name="Хеш JWT токена")
    ip_address = models.GenericIPAddressField(verbose_name="IP адрес")
    user_agent = models.TextField(verbose_name="User Agent")
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Последняя активность")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    # Новые поля для контроля доверия
    session_trusted = models.BooleanField(default=False, verbose_name="Доверенная сессия")
    trusted_at = models.DateTimeField(blank=True, null=True, verbose_name="Время получения доверия")
    first_login_at = models.DateTimeField(default=timezone.now, verbose_name="Первый вход")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Сессия пользователя"
        verbose_name_plural = "Сессии пользователей"
        ordering = ['-last_activity']
    
    def __str__(self):
        return f"Сессия {self.user.email} - {self.ip_address}"
    
    @property
    def is_expired(self):
        """Проверка истечения срока хранения (15 дней)"""
        return timezone.now() - self.created_at > timedelta(days=15)
    
    @property
    def days_since_first_login(self):
        """Количество дней с первого входа"""
        return (timezone.now() - self.first_login_at).days
    
    @property
    def can_manage_sessions(self):
        """Может ли сессия управлять другими сессиями"""
        return self.session_trusted and self.days_since_first_login >= 3
    
    def make_trusted(self):
        """Сделать сессию доверенной"""
        if not self.session_trusted and self.days_since_first_login >= 3:
            self.session_trusted = True
            self.trusted_at = timezone.now()
            self.save()
    
    @classmethod
    def is_valid_session(cls, session_key, user_id=None):
        """Проверить, существует ли активная сессия"""
        query = cls.objects.filter(
            session_key=session_key,
            is_active=True
        )
        if user_id:
            query = query.filter(user_id=user_id)
        return query.exists()
    
    @classmethod
    def is_valid_token(cls, token_hash, user_id=None):
        """Проверить, существует ли активная сессия с данным токеном"""
        query = cls.objects.filter(
            jwt_token_hash=token_hash,
            is_active=True
        )
        if user_id:
            query = query.filter(user_id=user_id)
        return query.exists()
    
    @property
    def device_info(self):
        """Информация об устройстве из User Agent"""
        ua = self.user_agent.lower()
        if 'mobile' in ua:
            return 'Мобильное устройство'
        elif 'tablet' in ua:
            return 'Планшет'
        elif 'windows' in ua:
            return 'Windows'
        elif 'mac' in ua:
            return 'MacOS'
        elif 'linux' in ua:
            return 'Linux'
        else:
            return 'Неизвестное устройство'
    
    @property
    def browser_info(self):
        """Информация о браузере из User Agent"""
        ua = self.user_agent.lower()
        if 'chrome' in ua:
            return 'Chrome'
        elif 'firefox' in ua:
            return 'Firefox'
        elif 'safari' in ua:
            return 'Safari'
        elif 'edge' in ua:
            return 'Edge'
        else:
            return 'Неизвестный браузер'


def cleanup_expired_sessions():
    """Очистка истекших сессий (вызывается периодически)"""
    cutoff_date = timezone.now() - timedelta(days=15)
    UserSession.objects.filter(created_at__lt=cutoff_date).delete() 