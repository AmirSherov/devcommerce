import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Any

from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied, ValidationError

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied as DRFPermissionDenied

from .models import (
    StorageContainer, StorageFile, UserStorageUsage, StorageAPILog
)
from .serializers import (
    StorageContainerSerializer, StorageContainerCreateSerializer,
    StorageFileSerializer, StorageFileUploadSerializer, StorageFileListSerializer,
    UserStorageUsageSerializer, StorageLimitsSerializer, StorageStatsSerializer,
    StorageAPILogSerializer
)
from .s3_utils import (
    upload_file_to_s3, delete_file_from_s3, get_file_url_from_s3,
    file_exists_in_s3, get_file_info_from_s3, get_bucket_size_from_s3
)
import os

logger = logging.getLogger(__name__)
User = get_user_model()


class StorageContainerView(APIView):
    """
    📦 API ДЛЯ УПРАВЛЕНИЯ КОНТЕЙНЕРАМИ ХРАНИЛИЩА
    
    GET /api/storage/containers/ - список контейнеров пользователя
    POST /api/storage/containers/ - создать новый контейнер
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение списка контейнеров пользователя"""
        try:
            # Получаем только контейнеры текущего пользователя
            containers = StorageContainer.objects.filter(
                user=request.user,
                is_active=True
            ).order_by('-created_at')
            
            # Пересчитываем статистику для каждого контейнера
            for container in containers:
                self._recalculate_container_stats(container)
            
            serializer = StorageContainerSerializer(containers, many=True)
            
            return Response({
                'success': True,
                'containers': serializer.data,
                'total_containers': containers.count()
            })
            
        except Exception as e:
            logger.error(f"[STORAGE CONTAINERS] Ошибка получения контейнеров: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения контейнеров'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Создание нового контейнера"""
        try:
            # Проверяем лимиты пользователя
            can_create, limit_message = self._check_container_limits(request.user)
            if not can_create:
                return Response({
                    'success': False,
                    'error': limit_message,
                    'error_code': 'CONTAINER_LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Валидируем данные
            serializer = StorageContainerCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем уникальность имени контейнера для пользователя
            name = serializer.validated_data['name']
            if StorageContainer.objects.filter(user=request.user, name=name).exists():
                return Response({
                    'success': False,
                    'error': 'Контейнер с таким именем уже существует',
                    'error_code': 'CONTAINER_NAME_EXISTS'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Создаем контейнер
            container = StorageContainer.objects.create(
                user=request.user,
                name=name,
                is_public=serializer.validated_data.get('is_public', False)
            )
            
            # Обновляем статистику
            self._update_user_stats(request.user, 'container_created')
            
            logger.info(f"[STORAGE CONTAINER] Создан контейнер '{name}' для {request.user.username}")
            
            return Response({
                'success': True,
                'container': StorageContainerSerializer(container).data,
                'message': 'Контейнер успешно создан'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER] Ошибка создания контейнера: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка создания контейнера'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_container_limits(self, user: User) -> tuple[bool, str]:
        """Проверка лимитов на создание контейнеров"""
        # Получаем текущее количество контейнеров пользователя
        containers_count = StorageContainer.objects.filter(
            user=user, 
            is_active=True
        ).count()
        
        # Лимиты по планам
        if user.plan == 'pro':
            max_containers = 100  # Pro: 100 контейнеров
        elif user.plan == 'premium':
            max_containers = 50  # Premium: 50 контейнеров
        else:
            max_containers = 10  # Standard: 10 контейнеров
        
        if containers_count >= max_containers:
            return False, f"Превышен лимит контейнеров ({max_containers}). Удалите ненужные контейнеры."
        
        return True, f"Можно создать еще {max_containers - containers_count} контейнеров"
    
    def _update_user_stats(self, user: User, action: str):
        """Обновление статистики пользователя"""
        today = timezone.now().date()
        
        usage, created = UserStorageUsage.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'bytes_used': 0,
                'files_count': 0,
                'containers_count': 0,
                'uploads_count': 0,
                'uploads_size': 0,
                'deletions_count': 0,
                'deletions_size': 0,
                'file_types_stats': {}
            }
        )
        
        if action == 'container_created':
            usage.containers_count += 1
        
        usage.save()
    
    def _recalculate_container_stats(self, container):
        """Пересчет статистики контейнера"""
        try:
            # Получаем активные файлы в контейнере
            files = StorageFile.objects.filter(
                container=container,
                is_active=True
            )
            
            # Пересчитываем статистику
            files_count = files.count()
            total_size = files.aggregate(total=Sum('file_size'))['total'] or 0
            
            # Обновляем контейнер только если данные изменились
            if container.files_count != files_count or container.total_size != total_size:
                container.files_count = files_count
                container.total_size = total_size
                container.save()
                logger.info(f"[STORAGE CONTAINER] Пересчитана статистика контейнера '{container.name}': {files_count} файлов, {total_size} байт")
                
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER] Ошибка пересчета статистики: {str(e)}")


class StorageContainerDetailView(APIView):
    """
    📦 API ДЛЯ УПРАВЛЕНИЯ КОНКРЕТНЫМ КОНТЕЙНЕРОМ
    
    GET /api/storage/containers/{id}/ - информация о контейнере
    PUT /api/storage/containers/{id}/ - обновить контейнер
    DELETE /api/storage/containers/{id}/ - удалить контейнер
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, container_id):
        """Получение информации о контейнере"""
        try:
            # Получаем контейнер с проверкой прав доступа
            container = get_object_or_404(
                StorageContainer,
                id=container_id,
                user=request.user,
                is_active=True
            )
            
            # Пересчитываем статистику контейнера
            self._recalculate_container_stats(container)
            
            serializer = StorageContainerSerializer(container)
            
            return Response({
                'success': True,
                'container': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER DETAIL] Ошибка получения контейнера: {str(e)}")
            return Response({
                'success': False,
                'error': 'Контейнер не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def _recalculate_container_stats(self, container):
        """Пересчет статистики контейнера"""
        try:
            # Получаем активные файлы в контейнере
            files = StorageFile.objects.filter(
                container=container,
                is_active=True
            )
            
            # Пересчитываем статистику
            files_count = files.count()
            total_size = files.aggregate(total=Sum('file_size'))['total'] or 0
            
            # Обновляем контейнер только если данные изменились
            if container.files_count != files_count or container.total_size != total_size:
                container.files_count = files_count
                container.total_size = total_size
                container.save()
                logger.info(f"[STORAGE CONTAINER] Пересчитана статистика контейнера '{container.name}': {files_count} файлов, {total_size} байт")
                
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER] Ошибка пересчета статистики: {str(e)}")
    
    def put(self, request, container_id):
        """Обновление контейнера"""
        try:
            # Получаем контейнер с проверкой прав доступа
            container = get_object_or_404(
                StorageContainer,
                id=container_id,
                user=request.user,
                is_active=True
            )
            
            # Валидируем данные
            serializer = StorageContainerCreateSerializer(data=request.data, partial=True)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем уникальность имени при изменении
            if 'name' in serializer.validated_data:
                new_name = serializer.validated_data['name']
                if StorageContainer.objects.filter(
                    user=request.user, 
                    name=new_name
                ).exclude(id=container_id).exists():
                    return Response({
                        'success': False,
                        'error': 'Контейнер с таким именем уже существует',
                        'error_code': 'CONTAINER_NAME_EXISTS'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            # Обновляем контейнер
            for field, value in serializer.validated_data.items():
                setattr(container, field, value)
            container.save()
            
            logger.info(f"[STORAGE CONTAINER] Обновлен контейнер '{container.name}' для {request.user.username}")
            
            return Response({
                'success': True,
                'container': StorageContainerSerializer(container).data,
                'message': 'Контейнер успешно обновлен'
            })
            
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER DETAIL] Ошибка обновления контейнера: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка обновления контейнера'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, container_id):
        """Удаление контейнера"""
        try:
            # Получаем контейнер с проверкой прав доступа
            container = get_object_or_404(
                StorageContainer,
                id=container_id,
                user=request.user,
                is_active=True
            )
            
            # Проверяем, есть ли файлы в контейнере
            if container.files_count > 0:
                return Response({
                    'success': False,
                    'error': 'Нельзя удалить контейнер с файлами. Сначала удалите все файлы.',
                    'error_code': 'CONTAINER_HAS_FILES'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Удаляем контейнер (мягкое удаление)
            container.is_active = False
            container.save()
            
            logger.info(f"[STORAGE CONTAINER] Удален контейнер '{container.name}' для {request.user.username}")
            
            return Response({
                'success': True,
                'message': 'Контейнер успешно удален'
            })
            
        except Exception as e:
            logger.error(f"[STORAGE CONTAINER DETAIL] Ошибка удаления контейнера: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка удаления контейнера'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StorageFileUploadView(APIView):
    """
    📁 API ДЛЯ ЗАГРУЗКИ ФАЙЛОВ
    
    POST /api/storage/containers/{id}/upload/ - загрузить файл в контейнер
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, container_id):
        """Загрузка файла в контейнер"""
        try:
            # Получаем контейнер с проверкой прав доступа
            container = get_object_or_404(
                StorageContainer,
                id=container_id,
                user=request.user,
                is_active=True
            )
            
            # Валидируем данные загрузки
            serializer = StorageFileUploadSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = serializer.validated_data['file']
            custom_filename = serializer.validated_data.get('filename')
            is_public = serializer.validated_data.get('is_public', False)
            
            # Проверяем лимиты файлов
            can_upload, limit_message = self._check_file_limits(request.user, uploaded_file.size)
            if not can_upload:
                return Response({
                    'success': False,
                    'error': limit_message,
                    'error_code': 'FILE_LIMIT_EXCEEDED'
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Проверяем размер файла
            max_file_size = 100 * 1024 * 1024  # 100MB максимум
            if uploaded_file.size > max_file_size:
                return Response({
                    'success': False,
                    'error': f'Файл слишком большой. Максимальный размер: {max_file_size // (1024*1024)}MB',
                    'error_code': 'FILE_TOO_LARGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Генерируем имя файла
            filename = custom_filename or uploaded_file.name
            if StorageFile.objects.filter(container=container, filename=filename).exists():
                # Добавляем суффикс если файл с таким именем уже существует
                name, ext = os.path.splitext(filename)
                counter = 1
                while StorageFile.objects.filter(container=container, filename=f"{name}_{counter}{ext}").exists():
                    counter += 1
                filename = f"{name}_{counter}{ext}"
            
            # Генерируем S3 ключ для файла
            s3_key = f"users/{request.user.id}/containers/{container.id}/{filename}"
            
            # Загружаем файл в S3
            upload_result = upload_file_to_s3(
                file_obj=uploaded_file,
                file_name=filename,
                container_name=f"user_{request.user.id}_container_{container.id}",
                content_type=uploaded_file.content_type
            )
            
            if not upload_result['success']:
                return Response({
                    'success': False,
                    'error': f"Ошибка загрузки в S3: {upload_result.get('error', 'Неизвестная ошибка')}",
                    'error_code': 'S3_UPLOAD_ERROR'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Создаем запись в базе данных
            storage_file = StorageFile.objects.create(
                container=container,
                filename=filename,
                original_filename=uploaded_file.name,
                s3_key=upload_result['s3_key'],
                file_size=uploaded_file.size,
                mime_type=uploaded_file.content_type,
                is_public=is_public,
                file_url=upload_result['file_url']
            )
            
            # Обновляем статистику контейнера
            container.files_count += 1
            container.total_size += uploaded_file.size
            container.save()
            
            # Обновляем статистику пользователя
            self._update_user_stats(request.user, 'file_uploaded', uploaded_file.size)
            
            logger.info(f"[STORAGE UPLOAD] Загружен файл '{filename}' в контейнер '{container.name}' для {request.user.username}")
            
            return Response({
                'success': True,
                'file': StorageFileSerializer(storage_file).data,
                'message': 'Файл успешно загружен'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"[STORAGE UPLOAD] Ошибка загрузки файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка загрузки файла'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _check_file_limits(self, user: User, file_size: int) -> tuple[bool, str]:
        """Проверка лимитов на загрузку файлов"""
        today = timezone.now().date()
        
        # Получаем статистику за сегодня
        usage, created = UserStorageUsage.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'bytes_used': 0,
                'files_count': 0,
                'containers_count': 0,
                'uploads_count': 0,
                'uploads_size': 0,
                'deletions_count': 0,
                'deletions_size': 0,
                'file_types_stats': {}
            }
        )
        
        # Лимиты по планам (только общий объем хранилища)
        if user.plan == 'pro':
            storage_limit = float('inf')  # Неограниченное хранилище
        elif user.plan == 'premium':
            storage_limit = 5 * 1024 * 1024 * 1024  # 5GB общее хранилище
        else:
            storage_limit = 100 * 1024 * 1024  # 100MB общее хранилище
        
        # Проверяем только общий лимит хранилища (убираем дневной лимит)
        if user.plan != 'pro' and usage.bytes_used + file_size > storage_limit:
            return False, f"Превышен лимит хранилища ({storage_limit // (1024*1024)}MB)"
        
        return True, "Можно загружать файл"
    
    def _update_user_stats(self, user: User, action: str, file_size: int = 0):
        """Обновление статистики пользователя"""
        today = timezone.now().date()
        
        usage, created = UserStorageUsage.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'bytes_used': 0,
                'files_count': 0,
                'containers_count': 0,
                'uploads_count': 0,
                'uploads_size': 0,
                'deletions_count': 0,
                'deletions_size': 0,
                'file_types_stats': {}
            }
        )
        
        if action == 'file_uploaded':
            usage.uploads_count += 1
            usage.uploads_size += file_size
            usage.bytes_used += file_size
            usage.files_count += 1
        
        usage.save()


class StorageFileListView(APIView):
    """
    📁 API ДЛЯ ПОЛУЧЕНИЯ СПИСКА ФАЙЛОВ
    
    GET /api/storage/containers/{id}/files/ - список файлов в контейнере
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, container_id):
        """Получение списка файлов в контейнере"""
        try:
            # Получаем контейнер с проверкой прав доступа
            container = get_object_or_404(
                StorageContainer,
                id=container_id,
                user=request.user,
                is_active=True
            )
            
            # Получаем файлы с пагинацией
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)  # Максимум 100 файлов за раз
            
            files = StorageFile.objects.filter(
                container=container,
                is_active=True
            ).order_by('-created_at')
            
            # Применяем пагинацию
            start = (page - 1) * page_size
            end = start + page_size
            files_page = files[start:end]
            
            serializer = StorageFileListSerializer(files_page, many=True)
            
            return Response({
                'success': True,
                'files': serializer.data,
                'pagination': {
                    'page': page,
                    'page_size': page_size,
                    'total_files': files.count(),
                    'total_pages': (files.count() + page_size - 1) // page_size
                }
            })
            
        except Exception as e:
            logger.error(f"[STORAGE FILES] Ошибка получения файлов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения файлов'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StorageFileDetailView(APIView):
    """
    📁 API ДЛЯ УПРАВЛЕНИЯ КОНКРЕТНЫМ ФАЙЛОМ
    
    GET /api/storage/files/{id}/ - информация о файле
    DELETE /api/storage/files/{id}/ - удалить файл
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, file_id):
        """Получение информации о файле"""
        try:
            # Получаем файл с проверкой прав доступа
            storage_file = get_object_or_404(
                StorageFile,
                id=file_id,
                container__user=request.user,
                container__is_active=True,
                is_active=True
            )
            
            serializer = StorageFileSerializer(storage_file)
            
            return Response({
                'success': True,
                'file': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[STORAGE FILE DETAIL] Ошибка получения файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Файл не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, file_id):
        """Удаление файла"""
        try:
            # Получаем файл с проверкой прав доступа
            storage_file = get_object_or_404(
                StorageFile,
                id=file_id,
                container__user=request.user,
                container__is_active=True,
                is_active=True
            )
            
            # Удаляем файл из S3
            delete_result = delete_file_from_s3(storage_file.s3_key)
            
            if not delete_result['success']:
                logger.warning(f"[STORAGE DELETE] Ошибка удаления из S3: {delete_result.get('error')}")
                # Даже если S3 удаление не удалось, помечаем как неактивный в БД
                # чтобы избежать проблем с консистентностью
            
            # Помечаем файл как неактивный
            storage_file.is_active = False
            storage_file.save()
            
            # Обновляем статистику контейнера
            container = storage_file.container
            container.files_count -= 1
            container.total_size -= storage_file.file_size
            container.save()
            
            # Обновляем статистику пользователя
            self._update_user_stats(request.user, 'file_deleted', storage_file.file_size)
            
            logger.info(f"[STORAGE FILE] Удален файл '{storage_file.filename}' для {request.user.username}")
            
            return Response({
                'success': True,
                'message': 'Файл успешно удален'
            })
            
        except Exception as e:
            logger.error(f"[STORAGE FILE DETAIL] Ошибка удаления файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка удаления файла'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_user_stats(self, user: User, action: str, file_size: int = 0):
        """Обновление статистики пользователя"""
        today = timezone.now().date()
        
        usage, created = UserStorageUsage.objects.get_or_create(
            user=user,
            date=today,
            defaults={
                'bytes_used': 0,
                'files_count': 0,
                'containers_count': 0,
                'uploads_count': 0,
                'uploads_size': 0,
                'deletions_count': 0,
                'deletions_size': 0,
                'file_types_stats': {}
            }
        )
        
        if action == 'file_deleted':
            usage.deletions_count += 1
            usage.deletions_size += file_size
            usage.bytes_used -= file_size
            usage.files_count -= 1
        
        usage.save()


class StorageLimitsView(APIView):
    """
    📊 API ДЛЯ ПОЛУЧЕНИЯ ЛИМИТОВ ХРАНИЛИЩА
    
    GET /api/storage/limits/ - информация о лимитах пользователя
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение информации о лимитах хранилища"""
        try:
            user = request.user
            today = timezone.now().date()
            
            # Получаем статистику за сегодня
            usage, created = UserStorageUsage.objects.get_or_create(
                user=user,
                date=today,
                defaults={
                    'bytes_used': 0,
                    'files_count': 0,
                    'containers_count': 0,
                    'uploads_count': 0,
                    'uploads_size': 0,
                    'deletions_count': 0,
                    'deletions_size': 0,
                    'file_types_stats': {}
                }
            )
            
            # Определяем план и лимиты
            plan = user.plan
            if user.plan == 'pro':
                storage_limit_mb = float('inf')  # Неограниченное хранилище
                api_access = True
            elif user.plan == 'premium':
                storage_limit_mb = 5 * 1024  # 5GB
                api_access = False
            else:
                storage_limit_mb = 100  # 100MB
                api_access = False
            
            # Обрабатываем неограниченное хранилище для Pro плана
            if storage_limit_mb == float('inf'):
                storage_limit_gb = float('inf')
                storage_used_mb = usage.bytes_used / (1024 * 1024)
                storage_used_gb = storage_used_mb / 1024
                storage_remaining_mb = float('inf')
                storage_remaining_gb = float('inf')
                usage_percentage = 0
                can_upload = True
            else:
                storage_limit_gb = storage_limit_mb / 1024
                storage_used_mb = usage.bytes_used / (1024 * 1024)
                storage_used_gb = storage_used_mb / 1024
                storage_remaining_mb = max(0, storage_limit_mb - storage_used_mb)
                storage_remaining_gb = storage_remaining_mb / 1024
                usage_percentage = (storage_used_mb / storage_limit_mb) * 100 if storage_limit_mb > 0 else 0
                can_upload = storage_remaining_mb > 0
            
            return Response({
                'success': True,
                'limits': {
                    'plan': plan,
                    'storage_limit_mb': storage_limit_mb,
                    'storage_limit_gb': storage_limit_gb,
                    'storage_used_mb': round(storage_used_mb, 2),
                    'storage_used_gb': round(storage_used_gb, 2),
                    'storage_remaining_mb': round(storage_remaining_mb, 2),
                    'storage_remaining_gb': round(storage_remaining_gb, 2),
                    'usage_percentage': round(usage_percentage, 1),
                    'can_upload': can_upload,
                    'api_access': api_access
                }
            })
            
        except Exception as e:
            logger.error(f"[STORAGE LIMITS] Ошибка получения лимитов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения лимитов'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class StorageStatsView(APIView):
    """
    📈 API ДЛЯ ПОЛУЧЕНИЯ СТАТИСТИКИ ХРАНИЛИЩА
    
    GET /api/storage/stats/ - статистика использования хранилища
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Получение статистики использования хранилища"""
        try:
            user = request.user
            
            # Общая статистика
            containers = StorageContainer.objects.filter(user=user, is_active=True)
            files = StorageFile.objects.filter(container__user=user, is_active=True)
            
            total_containers = containers.count()
            total_files = files.count()
            total_size = files.aggregate(total=Sum('file_size'))['total'] or 0
            total_size_mb = total_size / (1024 * 1024)
            total_size_gb = total_size_mb / 1024
            
            # Статистика по типам файлов
            images_count = files.filter(mime_type__startswith='image/').count()
            videos_count = files.filter(mime_type__startswith='video/').count()
            documents_count = files.filter(
                Q(mime_type__startswith='application/') | 
                Q(mime_type__startswith='text/')
            ).count()
            other_files_count = total_files - images_count - videos_count - documents_count
            
            # Популярные типы файлов
            popular_types = files.values('mime_type').annotate(
                count=Count('mime_type')
            ).order_by('-count')[:5]
            
            # Статистика загрузок
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            month_ago = today - timedelta(days=30)
            
            uploads_today = UserStorageUsage.objects.filter(
                user=user, date=today
            ).aggregate(count=Sum('uploads_count'))['count'] or 0
            
            uploads_this_week = UserStorageUsage.objects.filter(
                user=user, date__gte=week_ago
            ).aggregate(count=Sum('uploads_count'))['count'] or 0
            
            uploads_this_month = UserStorageUsage.objects.filter(
                user=user, date__gte=month_ago
            ).aggregate(count=Sum('uploads_count'))['count'] or 0
            
            return Response({
                'success': True,
                'stats': {
                    'total_containers': total_containers,
                    'total_files': total_files,
                    'total_size_mb': round(total_size_mb, 2),
                    'total_size_gb': round(total_size_gb, 2),
                    'images_count': images_count,
                    'videos_count': videos_count,
                    'documents_count': documents_count,
                    'other_files_count': other_files_count,
                    'popular_file_types': list(popular_types),
                    'uploads_today': uploads_today,
                    'uploads_this_week': uploads_this_week,
                    'uploads_this_month': uploads_this_month
                }
            })
            
        except Exception as e:
            logger.error(f"[STORAGE STATS] Ошибка получения статистики: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения статистики'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
