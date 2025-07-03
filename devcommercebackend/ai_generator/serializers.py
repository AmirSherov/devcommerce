from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import (
    TemplateAIGeneration, 
    TemplateAIStats, 
    GlobalTemplateAIStats
)

User = get_user_model()


class TemplateAIGenerationRequestSerializer(serializers.Serializer):
    """
    🤖 СЕРИАЛИЗАТОР ДЛЯ ЗАПРОСА AI ЗАПОЛНЕНИЯ ШАБЛОНА
    
    Принимает данные пользователя для персонализации HTML шаблона
    """
    
    project_title = serializers.CharField(
        max_length=200,
        help_text="Название проекта",
        error_messages={
            'required': 'Название проекта обязательно',
            'blank': 'Название проекта не может быть пустым',
            'max_length': 'Название проекта не должно превышать 200 символов'
        }
    )
    
    project_description = serializers.CharField(
        max_length=1000,
        help_text="Описание проекта",
        error_messages={
            'required': 'Описание проекта обязательно',
            'blank': 'Описание проекта не может быть пустым',
            'max_length': 'Описание проекта не должно превышать 1000 символов'
        }
    )
    
    user_data = serializers.CharField(
        help_text="Данные пользователя для AI заполнения (свободный формат: навыки, опыт, образование, контакты)",
        error_messages={
            'required': 'Данные пользователя обязательны',
            'blank': 'Данные пользователя не могут быть пустыми'
        }
    )
    
    def validate_project_title(self, value):
        """Валидация названия проекта"""
        cleaned_title = value.strip()
        if len(cleaned_title) < 3:
            raise serializers.ValidationError(
                "Название проекта должно содержать минимум 3 символа"
            )
        if len(cleaned_title) > 200:
            raise serializers.ValidationError(
                "Название проекта не должно превышать 200 символов"
            )
        return cleaned_title
    
    def validate_project_description(self, value):
        """Валидация описания проекта"""
        cleaned_description = value.strip()
        if len(cleaned_description) < 10:
            raise serializers.ValidationError(
                "Описание проекта должно содержать минимум 10 символов"
            )
        if len(cleaned_description) > 1000:
            raise serializers.ValidationError(
                "Описание проекта не должно превышать 1000 символов"
            )
        return cleaned_description
    
    def validate_user_data(self, value):
        """Валидация пользовательских данных"""
        cleaned_data = value.strip()
        if len(cleaned_data) < 20:
            raise serializers.ValidationError(
                "Данные пользователя слишком короткие (минимум 20 символов)"
            )
        if len(cleaned_data) > 5000:
            raise serializers.ValidationError(
                "Данные пользователя слишком длинные (максимум 5000 символов)"
            )
        return cleaned_data


class TemplateAIGenerationSerializer(serializers.ModelSerializer):
    """
    📊 СЕРИАЛИЗАТОР ДЛЯ МОДЕЛИ AI ГЕНЕРАЦИИ ШАБЛОНА
    
    Используется для отображения истории генераций пользователя
    """
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    template_category = serializers.CharField(source='template.category', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    portfolio_slug = serializers.CharField(source='portfolio_created.slug', read_only=True)
    portfolio_title = serializers.CharField(source='portfolio_created.title', read_only=True)
    duration = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = TemplateAIGeneration
        fields = [
            'id', 'user_username', 'template_title', 'template_category',
            'project_title', 'project_description', 'user_data',
            'status', 'status_display', 'portfolio_slug', 'portfolio_title',
            'response_time', 'tokens_used', 'error_message', 'duration',
            'created_at', 'started_at', 'completed_at'
        ]
        read_only_fields = [
            'id', 'user_username', 'template_title', 'template_category',
            'portfolio_slug', 'portfolio_title', 'duration', 'status_display',
            'created_at', 'started_at', 'completed_at'
        ]


class TemplateAIStatsSerializer(serializers.ModelSerializer):
    """
    📈 СЕРИАЛИЗАТОР ДЛЯ СТАТИСТИКИ AI ГЕНЕРАЦИЙ ПОЛЬЗОВАТЕЛЯ
    
    Показывает ежедневную статистику использования AI и обычных шаблонов
    """
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    ai_success_rate = serializers.ReadOnlyField()
    total_usage = serializers.ReadOnlyField()
    ai_success_rate_display = serializers.SerializerMethodField()
    total_ai_response_time_display = serializers.SerializerMethodField()
    
    class Meta:
        model = TemplateAIStats
        fields = [
            'id', 'user_username', 'date',
            'ai_requests_count', 'ai_successful_count', 'ai_failed_count',
            'regular_usage_count', 'total_ai_response_time', 'total_tokens_used',
            'popular_templates', 'ai_success_rate', 'ai_success_rate_display',
            'total_usage', 'total_ai_response_time_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user_username', 'ai_success_rate', 'total_usage',
            'ai_success_rate_display', 'total_ai_response_time_display',
            'created_at', 'updated_at'
        ]
    
    def get_ai_success_rate_display(self, obj):
        """Форматированный success rate"""
        return f"{obj.ai_success_rate:.1f}%"
    
    def get_total_ai_response_time_display(self, obj):
        """Форматированное время ответа"""
        if obj.total_ai_response_time:
            return f"{obj.total_ai_response_time:.2f}s"
        return "0.00s"


class GlobalTemplateAIStatsSerializer(serializers.ModelSerializer):
    """
    🌍 СЕРИАЛИЗАТОР ДЛЯ ГЛОБАЛЬНОЙ СТАТИСТИКИ AI
    
    Показывает общую статистику платформы по использованию AI
    """
    
    ai_vs_regular_ratio = serializers.ReadOnlyField()
    ai_success_rate = serializers.SerializerMethodField()
    average_ai_response_time_display = serializers.SerializerMethodField()
    
    class Meta:
        model = GlobalTemplateAIStats
        fields = [
            'id', 'date',
            'total_ai_requests', 'total_ai_successful', 'total_ai_failed',
            'total_regular_usage', 'active_ai_users', 'premium_users_count',
            'average_ai_response_time', 'total_tokens_consumed',
            'popular_templates_ai', 'popular_templates_regular',
            'error_distribution', 'ai_vs_regular_ratio',
            'ai_success_rate', 'average_ai_response_time_display',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'ai_vs_regular_ratio', 'ai_success_rate',
            'average_ai_response_time_display', 'created_at', 'updated_at'
        ]
    
    def get_ai_success_rate(self, obj):
        """Вычисляем success rate"""
        if obj.total_ai_requests > 0:
            return round((obj.total_ai_successful / obj.total_ai_requests) * 100, 1)
        return 0.0
    
    def get_average_ai_response_time_display(self, obj):
        """Форматированное среднее время ответа"""
        if obj.average_ai_response_time:
            return f"{obj.average_ai_response_time:.2f}s"
        return "0.00s"


class TemplateAILimitsSerializer(serializers.Serializer):
    """
    🔒 СЕРИАЛИЗАТОР ДЛЯ ЛИМИТОВ AI ГЕНЕРАЦИЙ
    
    Показывает информацию о лимитах пользователя
    """
    
    is_premium = serializers.BooleanField(read_only=True)
    daily_limit = serializers.IntegerField(read_only=True)
    used_today = serializers.IntegerField(read_only=True)
    remaining_today = serializers.IntegerField(read_only=True)
    next_reset = serializers.DateTimeField(read_only=True)
    can_generate = serializers.BooleanField(read_only=True)
    limit_message = serializers.CharField(read_only=True)
    regular_usage_today = serializers.IntegerField(read_only=True)
    total_usage_today = serializers.IntegerField(read_only=True)


class RegularUsageRequestSerializer(serializers.Serializer):
    """
    📝 СЕРИАЛИЗАТОР ДЛЯ УЧЕТА ОБЫЧНОГО ИСПОЛЬЗОВАНИЯ ШАБЛОНОВ
    
    Используется для отслеживания использования шаблонов без AI
    """
    
    template_id = serializers.IntegerField(
        help_text="ID шаблона, который был использован",
        error_messages={
            'required': 'ID шаблона обязателен',
            'invalid': 'ID шаблона должен быть числом'
        }
    )
    
    def validate_template_id(self, value):
        """Валидация ID шаблона"""
        if value <= 0:
            raise serializers.ValidationError(
                "ID шаблона должен быть положительным числом"
            )
        return value


class TemplateAIGenerationResponseSerializer(serializers.Serializer):
    """
    ✅ СЕРИАЛИЗАТОР ДЛЯ ОТВЕТА AI ГЕНЕРАЦИИ
    
    Возвращает результат генерации AI портфолио
    """
    
    success = serializers.BooleanField()
    portfolio_slug = serializers.CharField(required=False)
    portfolio_url = serializers.CharField(required=False)
    generation_id = serializers.IntegerField(required=False)
    response_time = serializers.FloatField(required=False)
    tokens_used = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False)
    error_code = serializers.CharField(required=False)
    message = serializers.CharField(required=False)


class TemplateAIStatsOverviewSerializer(serializers.Serializer):
    """
    🎯 СЕРИАЛИЗАТОР ДЛЯ ОБЩЕГО ОБЗОРА СТАТИСТИКИ ПОЛЬЗОВАТЕЛЯ
    
    Показывает краткую статистику использования AI
    """
    
    total_ai_generations = serializers.IntegerField()
    successful_generations = serializers.IntegerField()
    failed_generations = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField()
    total_tokens_used = serializers.IntegerField()
    favorite_templates = serializers.ListField()
    today_usage = serializers.DictField()
    limits_info = serializers.DictField() 