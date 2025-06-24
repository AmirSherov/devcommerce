from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Portfolio, PortfolioLike, PortfolioView

User = get_user_model()


class PortfolioListSerializer(serializers.ModelSerializer):
    """Serializer for portfolio list view"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_full_name = serializers.CharField(source='author.full_name', read_only=True)
    public_url = serializers.ReadOnlyField()
    file_urls = serializers.ReadOnlyField(source='get_file_urls')
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'description', 'slug',
            'author_username', 'author_full_name',
            'is_public', 'created_at', 'updated_at',
            'views', 'likes', 'tags',
            'public_url', 'file_urls'
        ]


class PortfolioDetailSerializer(serializers.ModelSerializer):
    """Serializer for portfolio detail view with code content"""
    author_username = serializers.CharField(source='author.username', read_only=True)
    author_full_name = serializers.CharField(source='author.full_name', read_only=True)
    public_url = serializers.ReadOnlyField()
    file_urls = serializers.ReadOnlyField(source='get_file_urls')
    
    class Meta:
        model = Portfolio
        fields = [
            'id', 'title', 'description', 'slug',
            'author_username', 'author_full_name',
            'html_content', 'css_content', 'js_content',
            'is_public', 'created_at', 'updated_at',
            'views', 'likes', 'tags',
            'public_url', 'file_urls'
        ]


class PortfolioCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new portfolio"""
    
    class Meta:
        model = Portfolio
        fields = [
            'title', 'description', 'html_content', 
            'css_content', 'js_content', 'is_public', 'tags'
        ]
    
    def validate_title(self, value):
        """Validate title"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value.strip()
    
    def validate(self, attrs):
        """Validate portfolio creation"""
        user = self.context['request'].user
        
        # Check portfolio limit
        user_portfolio_count = Portfolio.objects.filter(author=user).count()
        if user_portfolio_count >= 5:
            raise serializers.ValidationError("Максимальное количество портфолио: 5")
        
        return attrs
    
    def create(self, validated_data):
        """Create portfolio with S3 files"""
        from .s3_service import s3_service
        
        user = self.context['request'].user
        portfolio = Portfolio.objects.create(author=user, **validated_data)
        
        # Create files in S3
        s3_service.create_portfolio_files(portfolio)
        
        return portfolio


class PortfolioUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating portfolio"""
    
    class Meta:
        model = Portfolio
        fields = [
            'title', 'description', 'html_content', 
            'css_content', 'js_content', 'is_public', 'tags'
        ]
    
    def validate_title(self, value):
        """Validate title"""
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Название должно содержать минимум 3 символа")
        return value.strip()
    
    def update(self, instance, validated_data):
        """Update portfolio and sync to S3"""
        from .s3_service import s3_service
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Sync to S3 and check if successful
        s3_success = s3_service.sync_portfolio_to_s3(instance)
        if not s3_success:
            raise serializers.ValidationError("Ошибка сохранения файлов в S3")
        
        return instance


class PortfolioCodeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only code content (for live editing)"""
    
    class Meta:
        model = Portfolio
        fields = ['html_content', 'css_content', 'js_content']
    
    def update(self, instance, validated_data):
        """Update code content and sync to S3"""
        from .s3_service import s3_service
        
        # Track which files changed
        changed_files = []
        
        if 'html_content' in validated_data and instance.html_content != validated_data['html_content']:
            instance.html_content = validated_data['html_content']
            changed_files.append(('html', instance.html_file_key, instance.html_content))
        
        if 'css_content' in validated_data and instance.css_content != validated_data['css_content']:
            instance.css_content = validated_data['css_content']
            changed_files.append(('css', instance.css_file_key, instance.css_content))
        
        if 'js_content' in validated_data and instance.js_content != validated_data['js_content']:
            instance.js_content = validated_data['js_content']
            changed_files.append(('js', instance.js_file_key, instance.js_content))
        
        if changed_files:
            instance.save()
            
            # Update only changed files in S3
            for file_type, file_key, content in changed_files:
                s3_service.update_portfolio_file(file_key, content, file_type)
        
        return instance


class PortfolioLikeSerializer(serializers.ModelSerializer):
    """Serializer for portfolio likes"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = PortfolioLike
        fields = ['id', 'user_username', 'created_at']


class PortfolioStatsSerializer(serializers.Serializer):
    """Serializer for portfolio statistics"""
    total_portfolios = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    public_portfolios = serializers.IntegerField()
    private_portfolios = serializers.IntegerField()


class UserPortfolioStatsSerializer(serializers.Serializer):
    """Serializer for user's portfolio statistics"""
    portfolios_count = serializers.IntegerField()
    remaining_slots = serializers.IntegerField()
    total_views = serializers.IntegerField()
    total_likes = serializers.IntegerField()
    most_viewed_portfolio = PortfolioListSerializer(read_only=True)
    most_liked_portfolio = PortfolioListSerializer(read_only=True) 