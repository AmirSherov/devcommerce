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


class PersonalInfoSerializer(serializers.Serializer):
    """Персональная информация"""
    firstName = serializers.CharField(max_length=100, help_text="Имя")
    lastName = serializers.CharField(max_length=100, help_text="Фамилия")
    profession = serializers.CharField(max_length=200, help_text="Профессия/специализация")
    bio = serializers.CharField(required=False, allow_blank=True, help_text="О себе")
    location = serializers.CharField(required=False, allow_blank=True, help_text="Местоположение")

class EducationSerializer(serializers.Serializer):
    """Образование"""
    university = serializers.CharField(max_length=300, help_text="Учебное заведение")
    degree = serializers.CharField(required=False, allow_blank=True, help_text="Степень/квалификация")
    field = serializers.CharField(max_length=200, help_text="Специальность")
    graduationYear = serializers.CharField(required=False, allow_blank=True, help_text="Год окончания")
    diplomaImage = serializers.ImageField(required=False, help_text="Фото диплома")

class ExperienceSerializer(serializers.Serializer):
    """Опыт работы"""
    company = serializers.CharField(max_length=200, help_text="Компания")
    position = serializers.CharField(max_length=200, help_text="Должность")
    duration = serializers.CharField(max_length=100, help_text="Период работы")
    description = serializers.CharField(required=False, allow_blank=True, help_text="Описание обязанностей")
    achievements = serializers.ListField(
        child=serializers.CharField(max_length=300),
        required=False,
        default=list,
        help_text="Ключевые достижения"
    )

class SkillsSerializer(serializers.Serializer):
    """Навыки"""
    technical = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Технические навыки"
    )
    tools = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Инструменты и ПО"
    )
    languages = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Языки программирования"
    )
    soft = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Личные качества"
    )

class ProjectSerializer(serializers.Serializer):    
    """Проект"""
    name = serializers.CharField(max_length=200, help_text="Название проекта")
    description = serializers.CharField(required=False, allow_blank=True, help_text="Описание проекта")
    technologies = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list,
        help_text="Используемые технологии"
    )
    link = serializers.URLField(required=False, allow_blank=True, help_text="Ссылка на проект")

class ContactsSerializer(serializers.Serializer):
    """Контакты"""
    email = serializers.EmailField(help_text="Email для связи")
    phone = serializers.CharField(required=False, allow_blank=True, max_length=20, help_text="Телефон")
    linkedin = serializers.URLField(required=False, allow_blank=True, help_text="LinkedIn профиль")
    github = serializers.URLField(required=False, allow_blank=True, help_text="GitHub профиль")
    website = serializers.URLField(required=False, allow_blank=True, help_text="Личный сайт")
    telegram = serializers.CharField(required=False, allow_blank=True, max_length=50, help_text="Telegram")

class DesignPreferencesSerializer(serializers.Serializer):
    """Настройки дизайна"""
    style = serializers.ChoiceField(
        choices=[
            ('modern', 'Современный'),
            ('creative', 'Креативный'),
            ('minimal', 'Минималистичный'),
            ('corporate', 'Корпоративный'),
            ('dark', 'Темный'),
            ('colorful', 'Яркий'),
        ],
        default='modern',
        help_text="Стиль дизайна"
    )
    colorScheme = serializers.ChoiceField(
        choices=[
            ('professional', 'Профессиональная'),
            ('creative', 'Креативная'),
            ('minimal', 'Минимальная'),
            ('warm', 'Теплая'),
            ('cool', 'Холодная'),
            ('nature', 'Природная'),
        ],
        default='professional',
        help_text="Цветовая схема"
    )
    theme = serializers.ChoiceField(
        choices=[
            ('clean', 'Чистая'),
            ('bold', 'Смелая'),
            ('elegant', 'Элегантная'),
            ('playful', 'Игривая'),
            ('serious', 'Серьезная'),
        ],
        default='clean',
        help_text="Тема"
    )

class AIGenerationRequestSerializer(serializers.Serializer):
    """Сериализатор для запроса AI генерации персонального портфолио"""
    
    personal_info = PersonalInfoSerializer(help_text="Персональная информация")
    education = EducationSerializer(required=False, help_text="Образование")
    experience = ExperienceSerializer(many=True, required=False, help_text="Опыт работы")
    skills = SkillsSerializer(help_text="Навыки и технологии")
    projects = ProjectSerializer(many=True, required=False, help_text="Проекты и работы")
    contacts = ContactsSerializer(help_text="Контактная информация")
    design_preferences = DesignPreferencesSerializer(help_text="Настройки дизайна")
    profile_photo = serializers.ImageField(required=False, help_text="Фото профиля")
    
    def validate_personal_info(self, value):
        """Валидация персональной информации"""
        if not value.get('firstName') or not value.get('lastName'):
            raise serializers.ValidationError("Имя и фамилия обязательны")
        if not value.get('profession'):
            raise serializers.ValidationError("Укажите вашу профессию")
        return value
    
    def validate_skills(self, value):
        """Валидация навыков"""
        if not value.get('technical') or len(value.get('technical', [])) == 0:
            raise serializers.ValidationError("Добавьте хотя бы один технический навык")
        return value

    def validate_projects(self, value):
        """Валидация проектов"""
        if not value or len(value) == 0:
            raise serializers.ValidationError("Добавьте хотя бы один проект")
        return value 