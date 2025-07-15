import logging
import time
import os
from datetime import datetime, timedelta
from typing import Dict, Any

from django.db.models import Sum, Count, Q
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.http import HttpResponse, Http404

from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import (
    PublicAPIKey, PublicAPIRequest, PublicAPIUsage, PublicAPILimit
)
from .serializers import (
    PublicAPIKeySerializer, PublicAPIKeyCreateSerializer,
    PublicAPIRequestSerializer, PublicAPIUsageSerializer,
    PublicAPILimitSerializer, PublicFileUploadSerializer,
    PublicFileListSerializer, PublicFileDetailSerializer,
    PublicAPIStatsSerializer
)
from .authentication import PublicAPIAuthentication, PublicAPIPermission
from .s3_utils import (
    upload_file_to_public_s3, delete_file_from_public_s3, 
    get_file_url_from_public_s3, file_exists_in_public_s3
)
from storage.models import StorageContainer, StorageFile

logger = logging.getLogger(__name__)


class PublicAPIKeyView(APIView):
    """
    🔑 API ДЛЯ УПРАВЛЕНИЯ API КЛЮЧАМИ
    
    GET /api/public/storage/keys/ - информация о текущем API ключе
    POST /api/public/storage/keys/ - создать новый API ключ для контейнера
    """
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = []
    
    def get(self, request):
        """Получение информации о текущем API ключе"""
        try:
            user = request.user
            if isinstance(user, PublicAPIKey):
                api_key = user
            elif hasattr(user, 'is_authenticated') and user.is_authenticated:
                # Получаем ключ по container_id из query
                container_id = request.GET.get('container_id')
                if not container_id:
                    return Response({'success': False, 'error': 'container_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
                
                # Проверяем, что контейнер принадлежит пользователю
                from storage.models import StorageContainer
                container = StorageContainer.objects.filter(id=container_id, user=user).first()
                if not container:
                    return Response({'success': False, 'error': 'Контейнер не найден'}, status=status.HTTP_404_NOT_FOUND)
                
                # Ищем существующий PublicAPIKey или создаем новый
                api_key = PublicAPIKey.objects.filter(container=container).first()
                if not api_key:
                    # Автоматически создаем PublicAPIKey для контейнера
                    api_key = PublicAPIKey.objects.create(
                        container=container,
                        permissions={},
                        rate_limit_per_hour=1000,
                        max_file_size_mb=100
                    )
                    logger.info(f"[PUBLIC API KEY] Автоматически создан PublicAPIKey для контейнера '{container.name}'")
            else:
                return Response({'success': False, 'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
            
            serializer = PublicAPIKeySerializer(api_key)
            return Response({'success': True, 'api_key': serializer.data})
        except Exception as e:
            logger.error(f"[PUBLIC API KEY] Ошибка получения API ключа: {str(e)}")
            return Response({'success': False, 'error': 'Ошибка получения информации об API ключе'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Создание нового API ключа для контейнера"""
        try:
            user = request.user
            if not (hasattr(user, 'is_authenticated') and user.is_authenticated):
                return Response({'success': False, 'error': 'Требуется авторизация'}, status=status.HTTP_401_UNAUTHORIZED)
            container_id = request.data.get('container_id')
            if not container_id:
                return Response({'success': False, 'error': 'container_id обязателен'}, status=status.HTTP_400_BAD_REQUEST)
            from storage.models import StorageContainer
            container = StorageContainer.objects.filter(id=container_id, user=user).first()
            if not container:
                return Response({'success': False, 'error': 'Контейнер не найден'}, status=status.HTTP_404_NOT_FOUND)
            if hasattr(container, 'public_api_key'):
                return Response({'success': False, 'error': 'API ключ для этого контейнера уже существует', 'error_code': 'API_KEY_EXISTS'}, status=status.HTTP_400_BAD_REQUEST)
            serializer = PublicAPIKeyCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({'success': False, 'error': 'Некорректные данные', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
            api_key = PublicAPIKey.objects.create(
                container=container,
                permissions=serializer.validated_data.get('permissions', {}),
                rate_limit_per_hour=serializer.validated_data.get('rate_limit_per_hour', 1000),
                max_file_size_mb=serializer.validated_data.get('max_file_size_mb', 100)
            )
            logger.info(f"[PUBLIC API KEY] Создан API ключ для контейнера '{container.name}'")
            return Response({'success': True, 'api_key': PublicAPIKeySerializer(api_key).data, 'message': 'API ключ успешно создан'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"[PUBLIC API KEY] Ошибка создания API ключа: {str(e)}")
            return Response({'success': False, 'error': 'Ошибка создания API ключа'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicFileUploadView(APIView):
    """
    📁 API ДЛЯ ЗАГРУЗКИ ФАЙЛОВ ЧЕРЕЗ ПУБЛИЧНОЕ API
    
    POST /api/public/storage/upload/ - загрузить файл в контейнер
    """
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = [PublicAPIPermission]
    
    def post(self, request):
        """Загрузка файла через API"""
        try:
            api_key = request.user
            container = api_key.container
            
            # Валидируем данные загрузки
            serializer = PublicFileUploadSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': 'Некорректные данные',
                    'details': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            uploaded_file = serializer.validated_data['file']
            custom_filename = serializer.validated_data.get('filename')
            is_public = serializer.validated_data.get('is_public', False)
            metadata = serializer.validated_data.get('metadata', {})
            
            # Проверяем размер файла
            max_file_size = api_key.max_file_size_mb * 1024 * 1024
            if uploaded_file.size > max_file_size:
                return Response({
                    'success': False,
                    'error': f'Файл слишком большой. Максимальный размер: {api_key.max_file_size_mb}MB',
                    'error_code': 'FILE_TOO_LARGE'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Проверяем лимиты хранилища
            user_plan = container.user.plan
            if user_plan != 'pro':
                # Получаем лимиты для плана
                limits = PublicAPILimit.get_limits_for_plan(user_plan)
                storage_limit = limits.storage_limit_mb * 1024 * 1024
                
                # Проверяем текущее использование
                current_usage = StorageFile.objects.filter(
                    container=container,
                    is_active=True
                ).aggregate(total_size=Sum('file_size'))['total_size'] or 0
                
                if current_usage + uploaded_file.size > storage_limit:
                    return Response({
                        'success': False,
                        'error': f'Превышен лимит хранилища ({limits.storage_limit_mb}MB)',
                        'error_code': 'STORAGE_LIMIT_EXCEEDED'
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
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
            s3_key = f"users/{container.user.id}/containers/{container.id}/{filename}"
            
            # Загружаем файл в S3 через публичное API
            upload_result = upload_file_to_public_s3(
                file_obj=uploaded_file,
                file_name=filename,
                api_key=api_key.api_key,
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
            
            # Обновляем статистику API
            self._update_api_stats(api_key, 'file_uploaded', uploaded_file.size)
            
            logger.info(f"[PUBLIC API UPLOAD] Загружен файл '{filename}' через API для контейнера '{container.name}'")
            
            return Response({
                'success': True,
                'file': PublicFileDetailSerializer(storage_file).data,
                'message': 'Файл успешно загружен'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"[PUBLIC API UPLOAD] Ошибка загрузки файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка загрузки файла'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_api_stats(self, api_key: PublicAPIKey, action: str, file_size: int = 0):
        """Обновление статистики API"""
        today = timezone.now().date()
        
        usage, created = PublicAPIUsage.objects.get_or_create(
            api_key=api_key,
            date=today,
            defaults={
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'files_uploaded': 0,
                'files_downloaded': 0,
                'total_upload_size': 0,
                'total_download_size': 0,
                'total_response_time': 0.0,
                'average_response_time': 0.0,
                'popular_endpoints': {}
            }
        )
        
        if action == 'file_uploaded':
            usage.files_uploaded += 1
            usage.total_upload_size += file_size
        
        usage.save()


class PublicFileListView(APIView):
    """
    📁 API ДЛЯ ПОЛУЧЕНИЯ СПИСКА ФАЙЛОВ ЧЕРЕЗ ПУБЛИЧНОЕ API
    
    GET /api/public/storage/files/ - список файлов в контейнере
    """
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = [PublicAPIPermission]
    
    def get(self, request):
        """Получение списка файлов через API"""
        try:
            api_key = request.user
            container = api_key.container
            
            # Получаем параметры пагинации
            page = int(request.GET.get('page', 1))
            page_size = min(int(request.GET.get('page_size', 20)), 100)
            
            # Фильтры
            file_type = request.GET.get('type')  # image, video, document
            is_public = request.GET.get('public')
            
            # Базовый queryset
            files = StorageFile.objects.filter(
                container=container,
                is_active=True
            )
            
            # Применяем фильтры
            if file_type:
                if file_type == 'image':
                    files = files.filter(mime_type__startswith='image/')
                elif file_type == 'video':
                    files = files.filter(mime_type__startswith='video/')
                elif file_type == 'document':
                    files = files.filter(
                        Q(mime_type__startswith='application/') | 
                        Q(mime_type__startswith='text/')
                    )
            
            if is_public is not None:
                is_public_bool = is_public.lower() == 'true'
                files = files.filter(is_public=is_public_bool)
            
            # Сортировка
            sort_by = request.GET.get('sort', '-created_at')
            files = files.order_by(sort_by)
            
            # Применяем пагинацию
            start = (page - 1) * page_size
            end = start + page_size
            files_page = files[start:end]
            
            serializer = PublicFileListSerializer(files_page, many=True, context={'request': request})
            
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
            logger.error(f"[PUBLIC API FILES] Ошибка получения файлов: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения файлов'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PublicFileDetailView(APIView):
    """
    📁 API ДЛЯ ПОЛУЧЕНИЯ ИНФОРМАЦИИ О ФАЙЛЕ ЧЕРЕЗ ПУБЛИЧНОЕ API
    
    GET /api/public/storage/files/{id}/ - информация о файле
    DELETE /api/public/storage/files/{id}/ - удалить файл
    """
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = [PublicAPIPermission]
    
    def get(self, request, file_id):
        """Получение информации о файле"""
        try:
            api_key = request.user
            container = api_key.container
            
            # Получаем файл
            storage_file = get_object_or_404(
                StorageFile,
                id=file_id,
                container=container,
                is_active=True
            )
            
            serializer = PublicFileDetailSerializer(storage_file, context={'request': request})
            
            return Response({
                'success': True,
                'file': serializer.data
            })
            
        except Exception as e:
            logger.error(f"[PUBLIC API FILE DETAIL] Ошибка получения файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Файл не найден'
            }, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, file_id):
        """Удаление файла"""
        try:
            api_key = request.user
            container = api_key.container
            
            # Получаем файл
            storage_file = get_object_or_404(
                StorageFile,
                id=file_id,
                container=container,
                is_active=True
            )
            
            # Удаляем файл из S3
            delete_result = delete_file_from_public_s3(storage_file.s3_key)
            
            if not delete_result['success']:
                logger.warning(f"[PUBLIC API DELETE] Ошибка удаления из S3: {delete_result.get('error')}")
                # Даже если S3 удаление не удалось, помечаем как неактивный в БД
                # чтобы избежать проблем с консистентностью
            
            # Помечаем файл как неактивный
            storage_file.is_active = False
            storage_file.save()
            
            # Обновляем статистику контейнера
            container.files_count -= 1
            container.total_size -= storage_file.file_size
            container.save()
            
            # Обновляем статистику API
            self._update_api_stats(api_key, 'file_deleted', storage_file.file_size)
            
            logger.info(f"[PUBLIC API FILE] Удален файл '{storage_file.filename}' через API")
            
            return Response({
                'success': True,
                'message': 'Файл успешно удален'
            })
            
        except Exception as e:
            logger.error(f"[PUBLIC API FILE DETAIL] Ошибка удаления файла: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка удаления файла'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _update_api_stats(self, api_key: PublicAPIKey, action: str, file_size: int = 0):
        """Обновление статистики API"""
        today = timezone.now().date()
        
        usage, created = PublicAPIUsage.objects.get_or_create(
            api_key=api_key,
            date=today,
            defaults={
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'files_uploaded': 0,
                'files_downloaded': 0,
                'total_upload_size': 0,
                'total_download_size': 0,
                'total_response_time': 0.0,
                'average_response_time': 0.0,
                'popular_endpoints': {}
            }
        )
        
        if action == 'file_uploaded':
            usage.files_uploaded += 1
            usage.total_upload_size += file_size
        elif action == 'file_deleted':
            # При удалении файла не увеличиваем счетчики, так как файл уже был загружен
            pass
        
        usage.save()


class PublicFileDownloadView(APIView):
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = [PublicAPIPermission]

    def get(self, request, file_id):
        try:
            api_key = request.user
            container = api_key.container
            storage_file = get_object_or_404(StorageFile, id=file_id, container=container, is_active=True)
            # Получаем S3 ключ файла
            s3_key = storage_file.s3_key if hasattr(storage_file, 's3_key') else storage_file.file.name
            url = get_file_url_from_public_s3(s3_key)
            if not url:
                return Response({'success': False, 'error': 'Не удалось получить ссылку на файл'}, status=404)
            
            # Обновляем статистику API для скачивания
            self._update_api_stats(api_key, 'file_downloaded', storage_file.file_size)
            
            return redirect(url)
        except Exception as e:
            return Response({'success': False, 'error': str(e)}, status=404)
    
    def _update_api_stats(self, api_key: PublicAPIKey, action: str, file_size: int = 0):
        """Обновление статистики API"""
        today = timezone.now().date()
        
        usage, created = PublicAPIUsage.objects.get_or_create(
            api_key=api_key,
            date=today,
            defaults={
                'total_requests': 0,
                'successful_requests': 0,
                'failed_requests': 0,
                'files_uploaded': 0,
                'files_downloaded': 0,
                'total_upload_size': 0,
                'total_download_size': 0,
                'total_response_time': 0.0,
                'average_response_time': 0.0,
                'popular_endpoints': {}
            }
        )
        
        if action == 'file_downloaded':
            usage.files_downloaded += 1
            usage.total_download_size += file_size
        
        usage.save()


class PublicAPIStatsView(APIView):
    """
    📊 API ДЛЯ ПОЛУЧЕНИЯ СТАТИСТИКИ ПУБЛИЧНОГО API
    
    GET /api/public/storage/stats/ - статистика использования API
    GET /api/public/storage/stats/?container_id=<id> - статистика по конкретному контейнеру
    """
    authentication_classes = [PublicAPIAuthentication]
    permission_classes = []
    
    def get(self, request):
        """Получение статистики API"""
        try:
            user = request.user
            if isinstance(user, PublicAPIKey):
                container = user.container
                user_obj = container.user
            elif hasattr(user, 'is_authenticated') and user.is_authenticated:
                user_obj = user
            else:
                return Response({'success': False, 'error': 'Не авторизован'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Проверяем, запрашивается ли статистика по конкретному контейнеру
            container_id = request.GET.get('container_id')
            
            if container_id:
                # Статистика по конкретному контейнеру
                target_container = get_object_or_404(StorageContainer, id=container_id, user=user_obj)
                target_api_key = PublicAPIKey.objects.filter(container=target_container).first()
                
                if not target_api_key:
                    return Response({
                        'success': False,
                        'error': 'API ключ для указанного контейнера не найден'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                api_keys = [target_api_key]
                container_name = target_container.name
            else:
                # Общая статистика по всем контейнерам пользователя
                api_keys = PublicAPIKey.objects.filter(container__user=user_obj)
                container_name = "Все контейнеры"
            
            # Общая статистика запросов
            total_requests = PublicAPIRequest.objects.filter(api_key__in=api_keys).count()
            successful_requests = PublicAPIRequest.objects.filter(
                api_key__in=api_keys,
                status_code__lt=400
            ).count()
            failed_requests = total_requests - successful_requests
            success_rate = (successful_requests / total_requests * 100) if total_requests > 0 else 0
            
            # Статистика файлов
            containers = [ak.container for ak in api_keys]
            total_files = StorageFile.objects.filter(container__in=containers, is_active=True).count()
            files_uploaded = PublicAPIUsage.objects.filter(api_key__in=api_keys).aggregate(
                total=Sum('files_uploaded')
            )['total'] or 0
            files_downloaded = PublicAPIUsage.objects.filter(api_key__in=api_keys).aggregate(
                total=Sum('files_downloaded')
            )['total'] or 0
            
            # Размеры файлов
            total_upload_size = PublicAPIUsage.objects.filter(api_key__in=api_keys).aggregate(
                total=Sum('total_upload_size')
            )['total'] or 0
            total_download_size = PublicAPIUsage.objects.filter(api_key__in=api_keys).aggregate(
                total=Sum('total_download_size')
            )['total'] or 0
            
            # Производительность
            avg_response_time = PublicAPIUsage.objects.filter(api_key__in=api_keys).aggregate(
                avg=Sum('average_response_time') / Count('id')
            )['avg'] or 0
            
            # Популярные эндпоинты
            popular_endpoints = list(PublicAPIRequest.objects.filter(api_key__in=api_keys).values(
                'endpoint'
            ).annotate(count=Count('endpoint')).order_by('-count')[:10])
            
            # Топ ошибки
            top_errors = list(PublicAPIRequest.objects.filter(
                api_key__in=api_keys,
                status_code__gte=400
            ).values('status_code', 'error_code').annotate(
                count=Count('id')
            ).order_by('-count')[:5])
            
            # Последние запросы
            recent_requests = list(PublicAPIRequest.objects.filter(
                api_key__in=api_keys
            ).order_by('-created_at')[:10].values(
                'method', 'endpoint', 'status_code', 'response_time', 'created_at'
            ))
            
            # Usage по дням (за месяц)
            today = timezone.now().date()
            month_ago = today - timedelta(days=30)
            usage_by_day = PublicAPIUsage.objects.filter(
                api_key__in=api_keys,
                date__gte=month_ago
            ).order_by('date').values('date', 'total_requests', 'successful_requests', 
                                     'failed_requests', 'files_uploaded', 'files_downloaded',
                                     'total_upload_size', 'total_download_size', 'average_response_time')
            
            # Статистика по контейнерам (если общая статистика)
            containers_stats = []
            if not container_id:
                for ak in api_keys:
                    container_requests = PublicAPIRequest.objects.filter(api_key=ak).count()
                    container_files = StorageFile.objects.filter(container=ak.container, is_active=True).count()
                    containers_stats.append({
                        'container_name': ak.container.name,
                        'container_id': str(ak.container.id),
                        'total_requests': container_requests,
                        'total_files': container_files,
                        'last_used': ak.last_used_at.isoformat() if ak.last_used_at else None
                    })
            
            # Лимиты
            user_plan = user_obj.plan
            limits = PublicAPILimit.get_limits_for_plan(user_plan)
            
            # Осталось запросов в час
            hour_ago = timezone.now() - timedelta(hours=1)
            recent_requests_count = PublicAPIRequest.objects.filter(
                api_key__in=api_keys,
                created_at__gte=hour_ago
            ).count()
            requests_remaining = max(0, limits.requests_per_hour - recent_requests_count)
            
            # Статистика по типам файлов
            files_by_type = list(StorageFile.objects.filter(
                container__in=containers, 
                is_active=True
            ).values('mime_type').annotate(count=Count('mime_type')).order_by('-count')[:10])
            
            # Топ файлы по размеру
            top_files = list(StorageFile.objects.filter(
                container__in=containers, 
                is_active=True
            ).order_by('-file_size')[:5].values('filename', 'file_size', 'mime_type', 'created_at'))
            
            return Response({
                'success': True,
                'stats': {
                    'container_name': container_name,
                    'container_id': container_id,
                    
                    # Общая статистика
                    'total_requests': total_requests,
                    'successful_requests': successful_requests,
                    'failed_requests': failed_requests,
                    'success_rate': round(success_rate, 2),
                    
                    # Статистика файлов
                    'total_files': total_files,
                    'files_uploaded': files_uploaded,
                    'files_downloaded': files_downloaded,
                    'total_upload_size_mb': round(total_upload_size / (1024 * 1024), 2),
                    'total_download_size_mb': round(total_download_size / (1024 * 1024), 2),
                    
                    # Производительность
                    'average_response_time': round(avg_response_time, 3),
                    
                    # Популярные эндпоинты
                    'popular_endpoints': list(popular_endpoints),
                    
                    # Топ ошибки
                    'top_errors': list(top_errors),
                    
                    # Последние запросы
                    'recent_requests': list(recent_requests),
                    
                    # Usage по дням
                    'usage_by_day': list(usage_by_day),
                    
                    # Статистика по контейнерам
                    'containers_stats': containers_stats,
                    
                    # Статистика по типам файлов
                    'files_by_type': list(files_by_type),
                    
                    # Топ файлы
                    'top_files': list(top_files),
                    
                    # Лимиты
                    'rate_limit_per_hour': limits.requests_per_hour,
                    'requests_remaining': requests_remaining,
                    'max_file_size_mb': limits.max_file_size_mb,
                    'user_plan': user_plan
                }
            })
            
        except Exception as e:
            logger.error(f"[PUBLIC API STATS] Ошибка получения статистики: {str(e)}")
            return Response({
                'success': False,
                'error': 'Ошибка получения статистики'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
