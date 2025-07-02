from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PortfolioTemplate, TemplateUsage, TemplateLike

User = get_user_model()


class PortfolioTemplateListSerializer(serializers.ModelSerializer):
    """
    📋 СЕРИАЛИЗАТОР ДЛЯ СПИСКА ШАБЛОНОВ
    
    Легкий сериализатор для отображения сетки шаблонов
    """
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    demo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioTemplate
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'difficulty', 'difficulty_display', 'thumbnail_image', 'demo_url',
            'likes', 'views', 'uses', 'is_featured', 'is_premium',
            'created_by_username', 'created_at', 'tags', 'is_liked_by_user'
        ]
    
    def get_demo_url(self, obj):
        """Генерируем URL для предпросмотра шаблона"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/templates/{obj.id}/preview/')
        return f'/api/templates/{obj.id}/preview/'
    
    def get_is_liked_by_user(self, obj):
        """Проверяем лайкнул ли пользователь этот шаблон"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TemplateLike.objects.filter(
                template=obj, 
                user=request.user
            ).exists()
        return False


class PortfolioTemplateDetailSerializer(serializers.ModelSerializer):
    """
    📄 ДЕТАЛЬНЫЙ СЕРИАЛИЗАТОР ШАБЛОНА
    
    Полная информация о шаблоне включая код
    """
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    difficulty_display = serializers.CharField(source='get_difficulty_display', read_only=True)
    created_by_username = serializers.CharField(source='created_by.username', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    is_popular = serializers.BooleanField(read_only=True)
    usage_count = serializers.SerializerMethodField()
    demo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioTemplate
        fields = [
            'id', 'title', 'description', 'category', 'category_display',
            'difficulty', 'difficulty_display', 'html_code', 'css_code', 'js_code',
            'thumbnail_image', 'demo_url', 'tags', 'likes', 'views', 'uses',
            'is_active', 'is_featured', 'is_premium', 'is_popular',
            'created_by_username', 'created_at', 'updated_at',
            'is_liked_by_user', 'usage_count'
        ]
    
    def get_demo_url(self, obj):
        """Генерируем URL для предпросмотра шаблона"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/templates/{obj.id}/preview/')
        return f'/api/templates/{obj.id}/preview/'
    
    def get_is_liked_by_user(self, obj):
        """Проверяем лайкнул ли пользователь этот шаблон"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return TemplateLike.objects.filter(
                template=obj, 
                user=request.user
            ).exists()
        return False
    
    def get_usage_count(self, obj):
        """Получаем количество использований за последний месяц"""
        from django.utils import timezone
        from datetime import timedelta
        
        last_month = timezone.now() - timedelta(days=30)
        return TemplateUsage.objects.filter(
            template=obj,
            used_at__gte=last_month
        ).count()


class PortfolioTemplateCreateSerializer(serializers.ModelSerializer):
    """
    ✏️ СЕРИАЛИЗАТОР ДЛЯ СОЗДАНИЯ ШАБЛОНА
    """
    
    class Meta:
        model = PortfolioTemplate
        fields = [
            'title', 'description', 'category', 'difficulty',
            'html_code', 'css_code', 'js_code', 'thumbnail_image',
            'demo_url', 'tags', 'is_premium'
        ]
    
    def validate_title(self, value):
        """Валидация названия"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Название должно содержать минимум 3 символа"
            )
        return value.strip()
    
    def validate_description(self, value):
        """Валидация описания"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Описание должно содержать минимум 10 символов"
            )
        return value.strip()
    
    def validate_html_code(self, value):
        """Валидация HTML кода"""
        if not value.strip():
            raise serializers.ValidationError("HTML код обязателен")
        
        # Базовые проверки HTML
        if '<html' not in value.lower() and '<div' not in value.lower():
            raise serializers.ValidationError(
                "HTML код должен содержать валидную разметку"
            )
        
        return value.strip()
    
    def validate_css_code(self, value):
        """Валидация CSS кода"""
        if not value.strip():
            raise serializers.ValidationError("CSS код обязателен")
        
        return value.strip()
    
    def validate_tags(self, value):
        """Валидация тегов"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Теги должны быть списком")
        
        # Максимум 10 тегов
        if len(value) > 10:
            raise serializers.ValidationError("Максимум 10 тегов")
        
        # Валидация каждого тега
        validated_tags = []
        for tag in value:
            if isinstance(tag, str) and tag.strip():
                clean_tag = tag.strip().lower()
                if len(clean_tag) >= 2 and clean_tag not in validated_tags:
                    validated_tags.append(clean_tag)
        
        return validated_tags
    
    def create(self, validated_data):
        """Создание шаблона"""
        # Добавляем создателя
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)


class TemplateUsageSerializer(serializers.ModelSerializer):
    """
    📊 СЕРИАЛИЗАТОР ДЛЯ ИСПОЛЬЗОВАНИЙ ШАБЛОНА
    """
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    portfolio_title = serializers.CharField(source='portfolio_created.title', read_only=True)
    
    class Meta:
        model = TemplateUsage
        fields = [
            'id', 'template', 'template_title', 'user', 'user_username',
            'portfolio_created', 'portfolio_title', 'used_at'
        ]


class TemplateLikeSerializer(serializers.ModelSerializer):
    """
    👍 СЕРИАЛИЗАТОР ДЛЯ ЛАЙКОВ ШАБЛОНОВ
    """
    
    template_title = serializers.CharField(source='template.title', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = TemplateLike
        fields = [
            'id', 'template', 'template_title', 'user', 'user_username', 'liked_at'
        ]


class TemplateStatsSerializer(serializers.Serializer):
    """
    📈 СЕРИАЛИЗАТОР ДЛЯ СТАТИСТИКИ ШАБЛОНОВ
    """
    
    total_templates = serializers.IntegerField()
    active_templates = serializers.IntegerField()
    featured_templates = serializers.IntegerField()
    premium_templates = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_uses = serializers.IntegerField()
    popular_categories = serializers.ListField()
    recent_templates = serializers.ListField()


class UseTemplateSerializer(serializers.Serializer):
    """
    🎯 СЕРИАЛИЗАТОР ДЛЯ ИСПОЛЬЗОВАНИЯ ШАБЛОНА
    """
    
    template_id = serializers.IntegerField()
    portfolio_title = serializers.CharField(max_length=200, required=False)
    portfolio_description = serializers.CharField(required=False, allow_blank=True)
    
    def validate_template_id(self, value):
        """Валидация ID шаблона"""
        try:
            template = PortfolioTemplate.objects.get(
                id=value, 
                is_active=True
            )
        except PortfolioTemplate.DoesNotExist:
            raise serializers.ValidationError("Шаблон не найден или неактивен")
        
        return value 