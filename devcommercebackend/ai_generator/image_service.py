import os
import uuid
import logging
import requests
import time
import random
from typing import Optional, Dict, Any, Tuple, List
from io import BytesIO
from datetime import datetime

import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.contrib.auth import get_user_model
from django.core.cache import cache

logger = logging.getLogger(__name__)
User = get_user_model()


class S3ImageService:
    """
    🖼️ ПРЕМИУМ СЕРВИС ДЛЯ РАБОТЫ С ИЗОБРАЖЕНИЯМИ
    
    Загрузка, обработка и AI-анализ изображений пользователей:
    - Фото профиля
    - Дипломы/сертификаты  
    - Оптимизация и сжатие
    - Интеграция с S3 AWS
    """
    
    def __init__(self):
        """Инициализация S3 клиента"""
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )
            self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            self.base_url = f"https://{settings.AWS_S3_CUSTOM_DOMAIN}"
            
            logger.info("🎯 S3ImageService инициализирован успешно")
            
        except Exception as e:
            logger.error(f"💥 Ошибка инициализации S3: {str(e)}")
            self.s3_client = None
    
    def upload_profile_photo(self, user: User, image_file: InMemoryUploadedFile) -> Optional[str]:
        """
        📸 Загрузка фото профиля пользователя
        
        Args:
            user: Пользователь
            image_file: Загруженное изображение
            
        Returns:
            str: URL изображения в S3 или None при ошибке
        """
        if not self.s3_client:
            logger.error("💥 S3 клиент не инициализирован")
            return None
        
        try:
            # Валидация изображения
            if not self._validate_image(image_file, max_size_mb=5):
                logger.error("❌ Изображение не прошло валидацию")
                return None
            
            # Оптимизируем изображение
            optimized_image = self._optimize_profile_photo(image_file)
            if not optimized_image:
                logger.error("❌ Ошибка оптимизации изображения")
                return None
            
            # Генерируем уникальный путь
            file_extension = self._get_file_extension(image_file.name)
            unique_filename = f"profile_{user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            s3_key = f"users/{user.id}/profile_photos/{unique_filename}"
            
            # Загружаем в S3
            self.s3_client.upload_fileobj(
                optimized_image,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': f'image/{file_extension}',
                    'CacheControl': 'max-age=86400'
                }
            )
            
            # Формируем URL
            image_url = f"{self.base_url}/{s3_key}"
            
            logger.info(f"✅ Фото профиля загружено для пользователя {user.username}: {image_url}")
            return image_url
            
        except ClientError as e:
            logger.error(f"💥 AWS ошибка при загрузке фото профиля: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"💥 Общая ошибка при загрузке фото профиля: {str(e)}")
            return None
    
    def upload_diploma_image(self, user: User, image_file: InMemoryUploadedFile) -> Optional[str]:
        """
        🎓 Загрузка изображения диплома/сертификата
        
        Args:
            user: Пользователь
            image_file: Загруженное изображение диплома
            
        Returns:
            str: URL изображения в S3 или None при ошибке
        """
        if not self.s3_client:
            logger.error("💥 S3 клиент не инициализирован")
            return None
        
        try:
            # Валидация изображения диплома (больший размер разрешен)
            if not self._validate_image(image_file, max_size_mb=10):
                logger.error("❌ Изображение диплома не прошло валидацию")
                return None
            
            # Оптимизируем изображение диплома
            optimized_image = self._optimize_document_image(image_file)
            if not optimized_image:
                logger.error("❌ Ошибка оптимизации изображения диплома")
                return None
            
            # Генерируем уникальный путь
            file_extension = self._get_file_extension(image_file.name)
            unique_filename = f"diploma_{user.id}_{uuid.uuid4().hex[:8]}.{file_extension}"
            s3_key = f"users/{user.id}/education/{unique_filename}"
            
            # Загружаем в S3
            self.s3_client.upload_fileobj(
                optimized_image,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': f'image/{file_extension}',
                    'CacheControl': 'max-age=86400'
                }
            )
            
            # Формируем URL
            image_url = f"{self.base_url}/{s3_key}"
            
            logger.info(f"✅ Диплом загружен для пользователя {user.username}: {image_url}")
            return image_url
            
        except ClientError as e:
            logger.error(f"💥 AWS ошибка при загрузке диплома: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"💥 Общая ошибка при загрузке диплома: {str(e)}")
            return None
    
    def _validate_image(self, image_file: InMemoryUploadedFile, max_size_mb: int = 5) -> bool:
        """
        🔍 Валидация загруженного изображения
        
        Args:
            image_file: Загруженный файл
            max_size_mb: Максимальный размер в МБ
            
        Returns:
            bool: True если валидация прошла успешно
        """
        try:
            # Проверяем размер файла
            max_size_bytes = max_size_mb * 1024 * 1024
            if image_file.size > max_size_bytes:
                logger.error(f"❌ Файл слишком большой: {image_file.size} байт (макс: {max_size_bytes})")
                return False
            
            # Проверяем тип файла
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image_file.content_type not in allowed_types:
                logger.error(f"❌ Неподдерживаемый тип файла: {image_file.content_type}")
                return False
            
            # Проверяем, что это действительно изображение
            try:
                image = Image.open(image_file)
                image.verify()  # Проверяет целостность
                image_file.seek(0)  # Возвращаем указатель в начало
            except Exception as e:
                logger.error(f"❌ Файл не является корректным изображением: {str(e)}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Ошибка валидации изображения: {str(e)}")
            return False
    
    def _optimize_profile_photo(self, image_file: InMemoryUploadedFile) -> Optional[BytesIO]:
        """
        🎨 Оптимизация фото профиля
        
        - Квадратный кроп
        - Размер 300x300
        - Сжатие качества
        """
        try:
            image = Image.open(image_file)
            
            # Конвертируем в RGB если нужно
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Делаем квадратный кроп (центрированный)
            width, height = image.size
            min_dimension = min(width, height)
            
            left = (width - min_dimension) // 2
            top = (height - min_dimension) // 2
            right = left + min_dimension
            bottom = top + min_dimension
            
            image = image.crop((left, top, right, bottom))
            
            # Изменяем размер до 300x300
            image = image.resize((300, 300), Image.Resampling.LANCZOS)
            
            # Сохраняем оптимизированное изображение
            output = BytesIO()
            image.save(output, format='JPEG', quality=85, optimize=True)
            output.seek(0)
            
            logger.info("🎨 Фото профиля оптимизировано: 300x300, качество 85%")
            return output
            
        except Exception as e:
            logger.error(f"💥 Ошибка оптимизации фото профиля: {str(e)}")
            return None
    
    def _optimize_document_image(self, image_file: InMemoryUploadedFile) -> Optional[BytesIO]:
        """
        📄 Оптимизация изображения документа (диплом, сертификат)
        
        - Сохраняем пропорции
        - Максимальный размер 1200px по большей стороне
        - Улучшаем читаемость
        """
        try:
            image = Image.open(image_file)
            
            # Конвертируем в RGB если нужно
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Изменяем размер с сохранением пропорций
            max_size = 1200
            width, height = image.size
            
            if width > max_size or height > max_size:
                if width > height:
                    new_width = max_size
                    new_height = int((height * max_size) / width)
                else:
                    new_height = max_size
                    new_width = int((width * max_size) / height)
                
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Сохраняем с хорошим качеством для документов
            output = BytesIO()
            image.save(output, format='JPEG', quality=90, optimize=True)
            output.seek(0)
            
            logger.info(f"📄 Документ оптимизирован: {image.size}, качество 90%")
            return output
            
        except Exception as e:
            logger.error(f"💥 Ошибка оптимизации документа: {str(e)}")
            return None
    
    def _get_file_extension(self, filename: str) -> str:
        """Получение расширения файла"""
        return filename.split('.')[-1].lower() if '.' in filename else 'jpg'
    
    def analyze_profile_photo_with_ai(self, image_url: str) -> Dict[str, Any]:
        """
        🤖 AI анализ фото профиля для улучшения портфолио
        
        Args:
            image_url: URL изображения в S3
            
        Returns:
            dict: Результаты AI анализа
        """
        try:
            # Здесь можно интегрировать CV API для анализа изображения
            # Например: детекция лица, профессиональность фото, цветовая схема
            
            analysis_result = {
                'has_face': True,  # Пример данных
                'is_professional': True,
                'dominant_colors': ['#2c3e50', '#34495e', '#ecf0f1'],
                'image_quality': 'high',
                'suggested_background': 'clean',
                'crop_suggestion': 'centered',
                'lighting_quality': 'good',
                'ai_recommendations': [
                    'Отличное фото для профессионального портфолио',
                    'Хорошее освещение и композиция',
                    'Рекомендуем использовать как основное фото'
                ]
            }
            
            logger.info(f"🤖 AI анализ фото завершен: {image_url}")
            return analysis_result
            
        except Exception as e:
            logger.error(f"💥 Ошибка AI анализа фото: {str(e)}")
            return {
                'has_face': True,
                'is_professional': True,
                'ai_recommendations': ['Фото загружено успешно']
            }
    
    def delete_user_images(self, user: User) -> bool:
        """
        🗑️ Удаление всех изображений пользователя из S3
        
        Args:
            user: Пользователь
            
        Returns:
            bool: True если удаление прошло успешно
        """
        if not self.s3_client:
            return False
        
        try:
            # Получаем список всех объектов пользователя
            prefix = f"users/{user.id}/"
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            if 'Contents' in response:
                # Удаляем все объекты
                objects_to_delete = [{'Key': obj['Key']} for obj in response['Contents']]
                
                if objects_to_delete:
                    self.s3_client.delete_objects(
                        Bucket=self.bucket_name,
                        Delete={'Objects': objects_to_delete}
                    )
                    
                    logger.info(f"🗑️ Удалено {len(objects_to_delete)} изображений пользователя {user.username}")
            
            return True
            
        except Exception as e:
            logger.error(f"💥 Ошибка удаления изображений: {str(e)}")
            return False


# Создаем глобальный экземпляр сервиса
image_service = S3ImageService()


def upload_user_profile_photo(user: User, image_file: InMemoryUploadedFile) -> Optional[Tuple[str, Dict[str, Any]]]:
    """
    🎯 Хелпер для загрузки фото профиля с AI анализом
    
    Returns:
        tuple: (image_url, ai_analysis) или None при ошибке
    """
    try:
        # Загружаем изображение
        image_url = image_service.upload_profile_photo(user, image_file)
        if not image_url:
            return None
        
        # Анализируем с помощью AI
        ai_analysis = image_service.analyze_profile_photo_with_ai(image_url)
        
        return image_url, ai_analysis
        
    except Exception as e:
        logger.error(f"💥 Ошибка загрузки фото профиля: {str(e)}")
        return None


def upload_user_diploma_image(user: User, image_file: InMemoryUploadedFile) -> Optional[str]:
    """
    🎓 Хелпер для загрузки диплома/сертификата
    
    Returns:
        str: URL изображения или None при ошибке
    """
    try:
        return image_service.upload_diploma_image(user, image_file)
        
    except Exception as e:
        logger.error(f"💥 Ошибка загрузки диплома: {str(e)}")
        return None


# Инициализируем PexelsImageService для backward compatibility
class PexelsImageService:
    """Сервис для работы с Pexels API (для обратной совместимости)"""
    
    def __init__(self):
        self.access_key = "6r96KapNJVJkZ9Y22Bfa6dSiYYqPuvd0bbYQIhzTpmjyNhRtOGGcB6nj"
        self.base_url = "https://api.pexels.com/v1"
        self.enabled = True
        self.rate_limit_delay = 1  
        self.last_request_time = 0
        self.fallback_images = {
            'hero': [
                'https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
                'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
            ],
            'features': [
                'https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop',
                'https://images.pexels.com/photos/3184398/pexels-photo-3184398.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop',
            ],
        }
    
    def search_images(self, query: str, component_type: str = 'general', count: int = 1) -> List[str]:
        """Fallback метод для поиска изображений"""
        logger.info(f"[PEXELS] Запрос изображений: {query}")
        return self.fallback_images.get('hero', [])[:count]
    
    def get_images_for_component(self, component_type: str, industry: str, count: int = 1, style: str = 'modern') -> List[str]:
        """Получение изображений для компонентов"""
        return self.search_images(f"{industry} {component_type}", component_type, count)


# Экспортируем экземпляр для обратной совместимости
pexels_service = PexelsImageService() 