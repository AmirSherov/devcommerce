from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import UserProfile, UserNotificationSettings, UserSession

User = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Сериализатор для профиля пользователя"""
    
    age = serializers.ReadOnlyField()
    avatar_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'avatar', 'avatar_url', 'bio', 'location', 'birth_date', 'gender',
            'social_links', 'profile_visibility', 'projects_visibility', 
            'portfolio_visibility', 'notify_new_followers', 'age'
        ]
    
    def get_avatar_url(self, obj):
        """Получить URL аватара"""
        if obj.avatar:
            return obj.avatar.url
        return None
    
    def validate_social_links(self, value):
        """Валидация социальных ссылок"""
        allowed_keys = ['github', 'linkedin', 'twitter', 'instagram', 'website']
        
        for key in value.keys():
            if key not in allowed_keys:
                raise serializers.ValidationError(f"Неподдерживаемая социальная сеть: {key}")
        
        return value


class UserNotificationSettingsSerializer(serializers.ModelSerializer):
    """Сериализатор для настроек уведомлений"""
    
    class Meta:
        model = UserNotificationSettings
        fields = [
            'email_notifications', 'project_notifications', 
            'like_comment_notifications', 'template_notifications', 
            'weekly_newsletter'
        ]


class UserSessionSerializer(serializers.ModelSerializer):
    """Сериализатор для сессий пользователя"""
    
    device_info = serializers.ReadOnlyField()
    browser_info = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    is_current_session = serializers.SerializerMethodField()
    days_since_first_login = serializers.ReadOnlyField()
    can_manage_sessions = serializers.ReadOnlyField()
    session_trusted = serializers.ReadOnlyField()
    
    class Meta:
        model = UserSession
        fields = [
            'id', 'ip_address', 'user_agent', 'last_activity', 
            'is_active', 'created_at', 'device_info', 'browser_info',
            'is_expired', 'is_current_session', 'days_since_first_login',
            'can_manage_sessions', 'session_trusted'
        ]
        read_only_fields = ['id', 'ip_address', 'user_agent', 'last_activity', 
                           'created_at', 'device_info', 'browser_info', 'is_expired',
                           'days_since_first_login', 'can_manage_sessions', 'session_trusted']
    
    def get_is_current_session(self, obj):
        """Проверка, является ли это текущей сессией"""
        request = self.context.get('request')
        if request:
            # Проверяем X-Session-Key из заголовка, если он есть
            session_key_header = request.META.get('HTTP_X_SESSION_KEY')
            if session_key_header:
                return obj.session_key == session_key_header
            # Иначе сравниваем с request.session.session_key
            return obj.session_key == getattr(request.session, 'session_key', None)
        return False


class ChangePasswordSerializer(serializers.Serializer):
    """Сериализатор для смены пароля"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, min_length=8)
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        """Валидация паролей"""
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("Пароли не совпадают")
        return attrs
    
    def validate_current_password(self, value):
        """Проверка текущего пароля"""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value


class AvatarUploadSerializer(serializers.Serializer):
    """Сериализатор для загрузки аватара"""
    
    avatar = serializers.ImageField()
    
    def validate_avatar(self, value):
        """Валидация изображения"""
        # Проверка размера файла (максимум 5MB)
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Размер файла не должен превышать 5MB")
        
        # Проверка формата
        allowed_formats = ['image/jpeg', 'image/png', 'image/gif']
        if value.content_type not in allowed_formats:
            raise serializers.ValidationError("Поддерживаются только JPEG, PNG и GIF форматы")
        
        return value 