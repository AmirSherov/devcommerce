from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import AIGenerationRequest, AIGenerationStats, AIPromptTemplate

User = get_user_model()


class AIGenerateRequestSerializer(serializers.Serializer):
    """Serializer для запроса AI генерации"""
    
    title = serializers.CharField(
        max_length=200,
        help_text="Название проекта",
        error_messages={
            'max_length': 'Название проекта не должно превышать 200 символов',
            'required': 'Название проекта обязательно',
            'blank': 'Название проекта не может быть пустым'
        }
    )
    
    description = serializers.CharField(
        max_length=1000,
        required=False,
        allow_blank=True,
        help_text="Описание проекта (необязательно)",
        error_messages={
            'max_length': 'Описание не должно превышать 1000 символов'
        }
    )
    
    prompt = serializers.CharField(
        max_length=500,
        help_text="Промпт для AI генерации",
        error_messages={
            'max_length': 'Промпт не должен превышать 500 символов',
            'required': 'Промпт для AI обязателен',
            'blank': 'Промпт не может быть пустым'
        }
    )
    
    style = serializers.ChoiceField(
        choices=AIGenerationRequest.STYLE_CHOICES,
        default='modern',
        help_text="Стиль дизайна",
        error_messages={
            'invalid_choice': 'Выберите корректный стиль дизайна'
        }
    )
    
    tags = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        default=list,
        max_length=10,
        help_text="Теги проекта (максимум 10)",
        error_messages={
            'max_length': 'Максимум 10 тегов'
        }
    )
    
    def validate_title(self, value):
        """Валидация названия проекта"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название проекта должно содержать минимум 3 символа"
            )
        return value.strip()
    
    def validate_prompt(self, value):
        """Валидация промпта"""
        prompt = value.strip()
        if len(prompt) < 10:
            raise serializers.ValidationError(
                "Промпт должен содержать минимум 10 символов"
            )
        
        # Проверяем на спам/мусор
        spam_words = ['test', 'тест', 'asdf', '123']
        if prompt.lower() in spam_words:
            raise serializers.ValidationError(
                "Пожалуйста, введите более содержательный промпт"
            )
        
        return prompt
    
    def validate_tags(self, value):
        """Валидация тегов"""
        if value:
            # Очищаем и фильтруем теги
            clean_tags = []
            for tag in value:
                clean_tag = tag.strip().lower()
                if clean_tag and len(clean_tag) >= 2 and clean_tag not in clean_tags:
                    clean_tags.append(clean_tag)
            
            return clean_tags[:10]  # Максимум 10 тегов
        return []


class AIGenerateResponseSerializer(serializers.Serializer):
    """Serializer для ответа AI генерации"""
    
    success = serializers.BooleanField()
    portfolio = serializers.SerializerMethodField()
    request_id = serializers.IntegerField(required=False)
    response_time = serializers.FloatField(required=False)
    error = serializers.CharField(required=False)
    error_code = serializers.CharField(required=False)
    
    def get_portfolio(self, obj):
        """Получение данных портфолио"""
        if obj.get('success') and obj.get('portfolio'):
            from portfolio.serializers import PortfolioDetailSerializer
            return PortfolioDetailSerializer(obj['portfolio']).data
        return None


class AIGenerationRequestListSerializer(serializers.ModelSerializer):
    """Serializer для списка AI запросов пользователя"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    portfolio_title = serializers.CharField(source='portfolio_created.title', read_only=True)
    duration_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    style_display = serializers.CharField(source='get_style_display', read_only=True)
    
    class Meta:
        model = AIGenerationRequest
        fields = [
            'id', 'title', 'description', 'prompt', 'style', 'style_display',
            'status', 'status_display', 'user_username', 'portfolio_title',
            'response_time', 'duration_display', 'created_at', 'completed_at'
        ]
    
    def get_duration_display(self, obj):
        """Форматированное отображение длительности"""
        duration = obj.duration
        if duration:
            return f"{duration:.2f}s"
        return None


class AIGenerationStatsSerializer(serializers.ModelSerializer):
    """Serializer для статистики AI генераций пользователя"""
    
    success_rate_display = serializers.SerializerMethodField()
    average_response_time_display = serializers.SerializerMethodField()
    remaining_requests = serializers.SerializerMethodField()
    
    class Meta:
        model = AIGenerationStats
        fields = [
            'date', 'requests_count', 'successful_count', 'failed_count',
            'success_rate_display', 'average_response_time_display',
            'total_response_time', 'remaining_requests'
        ]
    
    def get_success_rate_display(self, obj):
        return f"{obj.success_rate}%"
    
    def get_average_response_time_display(self, obj):
        return f"{obj.average_response_time}s"
    
    def get_remaining_requests(self, obj):
        return max(0, 5 - obj.requests_count)


class AIPromptTemplateSerializer(serializers.ModelSerializer):
    """Serializer для шаблонов промптов"""
    
    user_username = serializers.CharField(source='user.username', read_only=True)
    style_display = serializers.CharField(source='get_style_display', read_only=True)
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    
    class Meta:
        model = AIPromptTemplate
        fields = [
            'id', 'name', 'prompt', 'category', 'category_display',
            'style', 'style_display', 'usage_count', 'success_rate',
            'is_public', 'is_featured', 'user_username', 'created_at'
        ]
        read_only_fields = ['usage_count', 'success_rate', 'user_username']
    
    def validate_name(self, value):
        """Валидация названия шаблона"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название шаблона должно содержать минимум 3 символа"
            )
        return value.strip()
    
    def validate_prompt(self, value):
        """Валидация промпта шаблона"""
        prompt = value.strip()
        if len(prompt) < 10:
            raise serializers.ValidationError(
                "Промпт должен содержать минимум 10 символов"
            )
        return prompt


class AIUserStatsSerializer(serializers.Serializer):
    """Serializer для общей статистики пользователя по AI"""
    
    total_requests = serializers.IntegerField()
    total_successful = serializers.IntegerField()
    total_failed = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField()
    total_portfolios_created = serializers.IntegerField()
    favorite_style = serializers.CharField()
    today_requests = serializers.IntegerField()
    remaining_today = serializers.IntegerField()
    most_used_prompts = serializers.ListField()


class AILimitsSerializer(serializers.Serializer):
    """Serializer для информации о лимитах пользователя"""
    
    is_premium = serializers.BooleanField()
    daily_limit = serializers.IntegerField()
    used_today = serializers.IntegerField()
    remaining_today = serializers.IntegerField()
    next_reset = serializers.DateTimeField()
    can_generate = serializers.BooleanField()
    limit_message = serializers.CharField()


class AIStyleStatsSerializer(serializers.Serializer):
    """Serializer для статистики по стилям"""
    
    style = serializers.CharField()
    count = serializers.IntegerField()
    success_rate = serializers.FloatField()
    average_response_time = serializers.FloatField() 