from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Project

User = get_user_model()


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор для автора проекта"""
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'full_name')


class ProjectListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка проектов (краткая информация)"""
    author = AuthorSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    is_from_same_author = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'title', 'description', 'project_photo', 'status',
            'technologies', 'likes', 'views', 'comments_count', 'author',
            'created_at', 'updated_at', 'slug', 'is_liked_by_user', 'is_from_same_author'
        )
        read_only_fields = ('id', 'likes', 'views', 'comments_count', 'created_at', 'updated_at', 'slug', 'is_liked_by_user', 'is_from_same_author')

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes_set.filter(user=request.user).exists()
        return False

    def get_is_from_same_author(self, obj):
        # Получаем ID автора текущего проекта из контекста
        current_author_id = self.context.get('current_author_id')
        if current_author_id:
            return obj.author.id == current_author_id
        return False


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детальной информации о проекте"""
    author = AuthorSerializer(read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = (
            'id', 'title', 'description', 'github_link', 'project_public_link',
            'project_photo', 'status', 'technologies', 'likes', 'views',
            'comments_count', 'author', 'created_at', 'updated_at', 'slug', 'is_liked_by_user'
        )
        read_only_fields = ('id', 'likes', 'views', 'comments_count', 'author', 'created_at', 'updated_at', 'slug', 'is_liked_by_user')

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes_set.filter(user=request.user).exists()
        return False


class ProjectCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания проекта"""
    
    class Meta:
        model = Project
        fields = (
            'title', 'description', 'github_link', 'project_public_link',
            'project_photo', 'status', 'technologies'
        )
        
    def validate_technologies(self, value):
        """Валидация поля technologies"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Technologies должно быть массивом")
        
        # Проверяем что все элементы - строки
        for tech in value:
            if not isinstance(tech, str):
                raise serializers.ValidationError("Все технологии должны быть строками")
        
        return value

    def create(self, validated_data):
        """Создание проекта с указанием автора"""
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['author'] = request.user
        return super().create(validated_data)


class ProjectUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления проекта"""
    
    class Meta:
        model = Project
        fields = (
            'title', 'description', 'github_link', 'project_public_link',
            'project_photo', 'technologies'
        )
        
    def validate_technologies(self, value):
        """Валидация поля technologies"""
        if not isinstance(value, list):
            raise serializers.ValidationError("Technologies должно быть массивом")
        
        for tech in value:
            if not isinstance(tech, str):
                raise serializers.ValidationError("Все технологии должны быть строками")
        
        return value


class ProjectStatusUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор для изменения статуса проекта"""
    
    class Meta:
        model = Project
        fields = ('status',)
        
    def validate_status(self, value):
        """Валидация статуса"""
        valid_statuses = [choice[0] for choice in Project.STATUS_CHOICES]
        if value not in valid_statuses:
            raise serializers.ValidationError(f"Статус должен быть одним из: {', '.join(valid_statuses)}")
        return value


class ProjectStatsSerializer(serializers.ModelSerializer):
    """Сериализатор для статистики проекта"""
    
    class Meta:
        model = Project
        fields = ('likes', 'views', 'comments_count')
        read_only_fields = ('likes', 'views', 'comments_count') 