from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Project
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateSerializer,
    ProjectUpdateSerializer,
    ProjectStatusUpdateSerializer,
)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_list(request):
    """
    GET /projects/ - получение всех публичных проектов с пагинацией
    """
    # Получаем только публичные проекты
    projects = Project.objects.filter(status='public').order_by('-created_at')
    
    # Параметры пагинации
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 12)
    
    try:
        page = int(page)
        page_size = int(page_size)
        if page_size > 50:  # Максимальный размер страницы
            page_size = 50
    except ValueError:
        page = 1
        page_size = 12
    
    # Поиск по названию и описанию
    search = request.GET.get('search', '')
    if search:
        projects = projects.filter(
            Q(title__icontains=search) | Q(description__icontains=search)
        )
    
    # Фильтр по технологиям
    technologies = request.GET.get('technologies', '')
    if technologies:
        tech_list = [tech.strip() for tech in technologies.split(',')]
        for tech in tech_list:
            projects = projects.filter(technologies__icontains=tech)
    
    # Пагинация
    paginator = Paginator(projects, page_size)
    try:
        projects_page = paginator.page(page)
    except:
        projects_page = paginator.page(1)
    
    serializer = ProjectListSerializer(projects_page.object_list, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': projects_page.has_next(),
        'has_previous': projects_page.has_previous()
    }, status=status.HTTP_200_OK)




@api_view(['GET'])
@permission_classes([AllowAny])
def other_projects(request, project_id):
    try:
        project = get_object_or_404(Project, id=project_id)
        project_author = project.author
        
        # Получаем все публичные проекты, кроме текущего
        all_public_projects = Project.objects.filter(
            status='public'
        ).exclude(id=project_id).order_by('-created_at')
        
        # Сериализуем все проекты с контекстом
        serializer = ProjectListSerializer(
            all_public_projects, 
            many=True, 
            context={
                'request': request,
                'current_author_id': project_author.id
            }
        )
        
        return Response({
            'results': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Ошибка при получении проектов',
            'details': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_projects(request):
    """
    GET /projects/me/ - получение всех проектов текущего пользователя
    """
    projects = Project.objects.filter(author=request.user).order_by('-created_at')
    
    # Пагинация
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 12)
    
    try:
        page = int(page)
        page_size = int(page_size)
        if page_size > 50:
            page_size = 50
    except ValueError:
        page = 1
        page_size = 12
    
    # Фильтр по статусу
    status_filter = request.GET.get('status', '')
    if status_filter and status_filter in ['public', 'profile_only', 'private']:
        projects = projects.filter(status=status_filter)
    
    paginator = Paginator(projects, page_size)
    try:
        projects_page = paginator.page(page)
    except:
        projects_page = paginator.page(1)
    
    serializer = ProjectDetailSerializer(projects_page.object_list, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': projects_page.has_next(),
        'has_previous': projects_page.has_previous()
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    """
    POST /projects/create/me/ - создание нового проекта
    """
    serializer = ProjectCreateSerializer(data=request.data, context={'request': request})
    
    if serializer.is_valid():
        try:
            project = serializer.save()
            response_serializer = ProjectDetailSerializer(project, context={'request': request})
            
            return Response({
                'message': 'Проект успешно создан',
                'project': response_serializer.data
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка при создании проекта',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_project(request, project_id):
    """
    PATCH /projects/me/{id}/ - частичное редактирование проекта
    """
    try:
        project = get_object_or_404(Project, id=project_id, author=request.user)
    except Project.DoesNotExist:
        return Response({
            'error': 'Проект не найден или у вас нет прав на его редактирование'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProjectUpdateSerializer(project, data=request.data, partial=True)
    
    if serializer.is_valid():
        try:
            project = serializer.save()
            response_serializer = ProjectDetailSerializer(project, context={'request': request})
            
            return Response({
                'message': 'Проект успешно обновлен',
                'project': response_serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка при обновлении проекта',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_project(request, project_id):
    """
    DELETE /projects/delete/me/{id}/ - удаление проекта
    """
    try:
        project = get_object_or_404(Project, id=project_id, author=request.user)
    except Project.DoesNotExist:
        return Response({
            'error': 'Проект не найден или у вас нет прав на его удаление'
        }, status=status.HTTP_404_NOT_FOUND)
    
    try:
        project_title = project.title
        project.delete()
        
        return Response({
            'message': f'Проект "{project_title}" успешно удален'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': 'Ошибка при удалении проекта',
            'details': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_project_status(request, project_id):
    """
    PATCH /projects/status/me/{id}/ - изменение статуса проекта
    """
    try:
        project = get_object_or_404(Project, id=project_id, author=request.user)
    except Project.DoesNotExist:
        return Response({
            'error': 'Проект не найден или у вас нет прав на изменение его статуса'
        }, status=status.HTTP_404_NOT_FOUND)
    
    serializer = ProjectStatusUpdateSerializer(project, data=request.data, partial=True)
    
    if serializer.is_valid():
        try:
            project = serializer.save()
            
            status_names = {
                'public': 'Публичный',
                'profile_only': 'Виден только в профиле',
                'private': 'Закрытый'
            }
            
            return Response({
                'message': f'Статус проекта изменен на "{status_names.get(project.status, project.status)}"',
                'project': {
                    'id': project.id,
                    'title': project.title,
                    'status': project.status
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Ошибка при изменении статуса проекта',
                'details': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def project_detail(request, project_id):
    """
    GET /projects/{slug}/ - получение проекта по slug
    """
    try:
        project = get_object_or_404(Project, id=project_id)
        # Проверяем видимость проекта
        if not project.is_visible_to_user(request.user if request.user.is_authenticated else None):
            return Response({
                'error': 'Проект не найден или недоступен'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Увеличиваем счетчик просмотров (только для аутентифицированных пользователей и не для автора)
        if request.user.is_authenticated and request.user != project.author:
            project.increment_views()
        
        serializer = ProjectDetailSerializer(project, context={'request': request})
        
        return Response({
            'project': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Project.DoesNotExist:
        return Response({
            'error': 'Проект не найден'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([AllowAny])
def user_projects(request, username):
    """
    GET /projects/user/{username}/ - получение проектов пользователя для его профиля
    """
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        user = get_object_or_404(User, username=username)
    except User.DoesNotExist:
        return Response({
            'error': 'Пользователь не найден'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Определяем какие проекты показывать
    if request.user.is_authenticated and request.user == user:
        # Владелец видит все свои проекты  
        projects = Project.objects.filter(author=user)
    else:
        # Остальные видят только публичные и profile_only
        projects = Project.objects.filter(
            author=user, 
            status__in=['public', 'profile_only']
        )
    
    projects = projects.order_by('-created_at')
    
    # Пагинация
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 12)
    
    try:
        page = int(page)
        page_size = int(page_size)
        if page_size > 50:
            page_size = 50
    except ValueError:
        page = 1
        page_size = 12
    
    paginator = Paginator(projects, page_size)
    try:
        projects_page = paginator.page(page)
    except:
        projects_page = paginator.page(1)
    
    serializer = ProjectListSerializer(projects_page.object_list, many=True, context={'request': request})
    
    return Response({
        'results': serializer.data,
        'count': paginator.count,
        'page': page,
        'page_size': page_size,
        'total_pages': paginator.num_pages,
        'has_next': projects_page.has_next(),
        'has_previous': projects_page.has_previous(),
        'user': {
            'id': user.id,
            'username': user.username,
            'full_name': user.full_name
        }
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_project_like(request, project_id):
    """POST /projects/toggle-like/<id>/ – лайк или дизлайк проекта"""
    project = get_object_or_404(Project, id=project_id)

    from .models import ProjectLike  # локальный импорт, чтобы избежать циклов

    like_obj, created = ProjectLike.objects.get_or_create(project=project, user=request.user)

    if created:
        project.increment_likes()
        liked = True
    else:
        like_obj.delete()
        project.decrement_likes()
        liked = False

    return Response({
        'likes': project.likes,
        'is_liked_by_user': liked
    }, status=status.HTTP_200_OK)
