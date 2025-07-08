from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Project, ProjectComment, ProjectCommentLike
from .comments_serializers import ProjectCommentSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def get_project_comments(request, project_id):
    """Получить все комментарии к проекту (сначала закреплённые, потом обычные, с вложенностью)"""
    project = get_object_or_404(Project, id=project_id)
    pinned = ProjectComment.objects.filter(project=project, parent=None, is_pinned=True).order_by('created_at')
    not_pinned = ProjectComment.objects.filter(project=project, parent=None, is_pinned=False).order_by('created_at')
    comments = list(pinned) + list(not_pinned)
    serializer = ProjectCommentSerializer(comments, many=True, context={'request': request})
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project_comment(request, project_id):
    """Создать комментарий (или вложенный) к проекту"""
    project = get_object_or_404(Project, id=project_id)
    data = request.data.copy()
    data['project'] = str(project.id)
    serializer = ProjectCommentSerializer(data=data, context={'request': request})
    if serializer.is_valid():
        serializer.save(author=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_project_comment(request, comment_id):
    """Редактировать комментарий"""
    comment = get_object_or_404(ProjectComment, id=comment_id, author=request.user)
    serializer = ProjectCommentSerializer(comment, data=request.data, partial=True, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project_comment(request, comment_id):
    """Удалить комментарий (жёстко)"""
    comment = get_object_or_404(ProjectComment, id=comment_id, author=request.user)
    comment.delete()
    return Response({'success': True})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_project_comment(request, comment_id):
    """Лайк/дизлайк комментария"""
    comment = get_object_or_404(ProjectComment, id=comment_id)
    like, created = ProjectCommentLike.objects.get_or_create(comment=comment, user=request.user)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return Response({'liked': liked, 'likes_count': comment.likes_set.count()})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pin_project_comment(request, comment_id):
    """Закрепить/открепить комментарий (только автор проекта или админ)"""
    comment = get_object_or_404(ProjectComment, id=comment_id)
    project = comment.project
    if request.user != project.author and not request.user.is_staff:
        return Response({'error': 'Нет прав'}, status=403)
    comment.is_pinned = not comment.is_pinned
    comment.save()
    return Response({'is_pinned': comment.is_pinned}) 