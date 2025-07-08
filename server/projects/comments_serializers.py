from rest_framework import serializers
from .models import ProjectComment, ProjectCommentLike
from django.contrib.auth import get_user_model

User = get_user_model()

class ProjectCommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectCommentLike
        fields = ('id', 'user', 'created_at')
        read_only_fields = ('id', 'user', 'created_at')

class ProjectCommentSerializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    is_liked_by_user = serializers.SerializerMethodField()
    replies = serializers.SerializerMethodField()

    class Meta:
        model = ProjectComment
        fields = (
            'id', 'project', 'author', 'text', 'created_at', 'updated_at',
            'parent', 'likes_count', 'is_liked_by_user', 'is_pinned', 'replies'
        )
        read_only_fields = ('id', 'author', 'created_at', 'updated_at', 'likes_count', 'is_liked_by_user', 'is_pinned', 'replies')

    def get_author(self, obj):
        return {
            'id': obj.author.id,
            'username': obj.author.username,
            'full_name': getattr(obj.author, 'full_name', obj.author.get_full_name() or obj.author.username)
        }

    def get_likes_count(self, obj):
        return obj.likes_set.count()

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes_set.filter(user=request.user).exists()
        return False

    def get_replies(self, obj):
        # Вложенные комментарии (только 1 уровень)
        replies_qs = obj.replies.filter(parent=obj, is_pinned=False).order_by('created_at')
        return ProjectCommentSerializer(replies_qs, many=True, context=self.context).data 