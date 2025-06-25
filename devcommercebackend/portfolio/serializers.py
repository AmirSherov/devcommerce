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
        """Create portfolio"""
        user = self.context['request'].user
        portfolio = Portfolio.objects.create(author=user, **validated_data)
        
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
        """Update portfolio"""
        
        # Update instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance


class PortfolioCodeUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating only code content (for live editing)"""
    
    class Meta:
        model = Portfolio
        fields = ['html_content', 'css_content', 'js_content']
    
    def update(self, instance, validated_data):
        """Update code content"""
        
        # Update instance with new data
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
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