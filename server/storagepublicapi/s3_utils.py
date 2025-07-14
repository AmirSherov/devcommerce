import boto3
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from botocore.exceptions import ClientError, NoCredentialsError
import logging
from typing import Optional, Dict, Any, List
import mimetypes
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class PublicS3StorageManager:
    """Менеджер для работы с S3 хранилищем для публичного API"""
    
    def __init__(self):
        self.s3_client = None
        self.bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        self.region_name = settings.AWS_S3_REGION_NAME
        
        # Инициализация S3 клиента
        try:
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=self.region_name
            )
        except Exception as e:
            logger.error(f"Ошибка инициализации S3 клиента для публичного API: {e}")
            self.s3_client = None
    
    def _get_s3_key(self, file_path: str, api_key: str = None) -> str:
        """Генерирует S3 ключ для файла публичного API"""
        if api_key:
            return f"public_api/{api_key}/{file_path}"
        return f"public_api/{file_path}"
    
    def upload_file(self, file_obj, file_name: str, api_key: str = None, 
                   content_type: str = None) -> Dict[str, Any]:
        """
        Загружает файл в S3 через публичное API
        
        Args:
            file_obj: Файловый объект
            file_name: Имя файла
            api_key: API ключ (опционально)
            content_type: MIME тип файла (опционально)
            
        Returns:
            Dict с результатом операции
        """
        try:
            if not self.s3_client:
                return {"success": False, "error": "S3 клиент не инициализирован"}
            
            # Определяем MIME тип если не передан
            if not content_type:
                content_type, _ = mimetypes.guess_type(file_name)
                if not content_type:
                    content_type = 'application/octet-stream'
            
            # Генерируем S3 ключ
            s3_key = self._get_s3_key(file_name, api_key)
            
            # Загружаем файл
            self.s3_client.upload_fileobj(
                file_obj,
                self.bucket_name,
                s3_key,
                ExtraArgs={
                    'ContentType': content_type,
                    'ACL': 'private'
                }
            )
            
            # Генерируем URL для доступа
            file_url = self._generate_presigned_url(s3_key)
            
            return {
                "success": True,
                "file_url": file_url,
                "s3_key": s3_key,
                "bucket": self.bucket_name,
                "content_type": content_type,
                "file_size": getattr(file_obj, 'size', 0)
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Ошибка загрузки файла в S3 (публичное API): {error_code} - {e}")
            return {"success": False, "error": f"S3 ошибка: {error_code}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при загрузке файла (публичное API): {e}")
            return {"success": False, "error": str(e)}
    
    def delete_file(self, s3_key: str) -> Dict[str, Any]:
        """
        Удаляет файл из S3
        
        Args:
            s3_key: S3 ключ файла
            
        Returns:
            Dict с результатом операции
        """
        try:
            if not self.s3_client:
                return {"success": False, "error": "S3 клиент не инициализирован"}
            
            self.s3_client.delete_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {"success": True, "deleted_key": s3_key}
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Ошибка удаления файла из S3 (публичное API): {error_code} - {e}")
            return {"success": False, "error": f"S3 ошибка: {error_code}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при удалении файла (публичное API): {e}")
            return {"success": False, "error": str(e)}
    
    def _generate_presigned_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Генерирует presigned URL для доступа к файлу
        
        Args:
            s3_key: S3 ключ файла
            expiration: Время жизни URL в секундах (по умолчанию 1 час)
            
        Returns:
            Presigned URL
        """
        try:
            if not self.s3_client:
                return ""
            
            url = self.s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.bucket_name,
                    'Key': s3_key
                },
                ExpiresIn=expiration
            )
            return url
        except Exception as e:
            logger.error(f"Ошибка генерации presigned URL (публичное API): {e}")
            return ""
    
    def get_file_url(self, s3_key: str, expiration: int = 3600) -> str:
        """
        Получает URL для доступа к файлу
        
        Args:
            s3_key: S3 ключ файла
            expiration: Время жизни URL в секундах
            
        Returns:
            URL для доступа к файлу
        """
        return self._generate_presigned_url(s3_key, expiration)
    
    def file_exists(self, s3_key: str) -> bool:
        """
        Проверяет существование файла в S3
        
        Args:
            s3_key: S3 ключ файла
            
        Returns:
            True если файл существует, False в противном случае
        """
        try:
            if not self.s3_client:
                return False
            
            self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            return True
        except ClientError as e:
            if e.response['Error']['Code'] == '404':
                return False
            logger.error(f"Ошибка проверки существования файла (публичное API): {e}")
            return False
        except Exception as e:
            logger.error(f"Неожиданная ошибка при проверке файла (публичное API): {e}")
            return False
    
    def get_file_info(self, s3_key: str) -> Dict[str, Any]:
        """
        Получает информацию о файле в S3
        
        Args:
            s3_key: S3 ключ файла
            
        Returns:
            Dict с информацией о файле
        """
        try:
            if not self.s3_client:
                return {"success": False, "error": "S3 клиент не инициализирован"}
            
            response = self.s3_client.head_object(
                Bucket=self.bucket_name,
                Key=s3_key
            )
            
            return {
                "success": True,
                "size": response.get('ContentLength', 0),
                "content_type": response.get('ContentType', ''),
                "last_modified": response.get('LastModified'),
                "etag": response.get('ETag', ''),
                "metadata": response.get('Metadata', {})
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Ошибка получения информации о файле (публичное API): {error_code} - {e}")
            return {"success": False, "error": f"S3 ошибка: {error_code}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении информации о файле (публичное API): {e}")
            return {"success": False, "error": str(e)}
    
    def list_files(self, prefix: str = "", max_keys: int = 1000) -> Dict[str, Any]:
        """
        Получает список файлов в S3 с заданным префиксом
        
        Args:
            prefix: Префикс для поиска файлов
            max_keys: Максимальное количество файлов
            
        Returns:
            Dict со списком файлов
        """
        try:
            if not self.s3_client:
                return {"success": False, "error": "S3 клиент не инициализирован"}
            
            response = self.s3_client.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=max_keys
            )
            
            files = []
            if 'Contents' in response:
                for obj in response['Contents']:
                    files.append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'],
                        'etag': obj['ETag']
                    })
            
            return {
                "success": True,
                "files": files,
                "count": len(files),
                "is_truncated": response.get('IsTruncated', False)
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Ошибка получения списка файлов (публичное API): {error_code} - {e}")
            return {"success": False, "error": f"S3 ошибка: {error_code}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении списка файлов (публичное API): {e}")
            return {"success": False, "error": str(e)}
    
    def get_bucket_size(self, prefix: str = "") -> Dict[str, Any]:
        """
        Получает общий размер файлов в бакете с заданным префиксом
        
        Args:
            prefix: Префикс для подсчета размера
            
        Returns:
            Dict с информацией о размере
        """
        try:
            if not self.s3_client:
                return {"success": False, "error": "S3 клиент не инициализирован"}
            
            total_size = 0
            file_count = 0
            
            paginator = self.s3_client.get_paginator('list_objects_v2')
            page_iterator = paginator.paginate(
                Bucket=self.bucket_name,
                Prefix=prefix
            )
            
            for page in page_iterator:
                if 'Contents' in page:
                    for obj in page['Contents']:
                        total_size += obj['Size']
                        file_count += 1
            
            return {
                "success": True,
                "total_size": total_size,
                "file_count": file_count,
                "size_mb": round(total_size / (1024 * 1024), 2),
                "size_gb": round(total_size / (1024 * 1024 * 1024), 2)
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            logger.error(f"Ошибка получения размера бакета (публичное API): {error_code} - {e}")
            return {"success": False, "error": f"S3 ошибка: {error_code}"}
        except Exception as e:
            logger.error(f"Неожиданная ошибка при получении размера бакета (публичное API): {e}")
            return {"success": False, "error": str(e)}


# Создаем глобальный экземпляр менеджера
public_s3_manager = PublicS3StorageManager()


# Удобные функции для быстрого доступа
def upload_file_to_public_s3(file_obj, file_name: str, api_key: str = None, 
                            content_type: str = None) -> Dict[str, Any]:
    """Загружает файл в S3 через публичное API"""
    return public_s3_manager.upload_file(file_obj, file_name, api_key, content_type)


def delete_file_from_public_s3(s3_key: str) -> Dict[str, Any]:
    """Удаляет файл из S3 через публичное API"""
    return public_s3_manager.delete_file(s3_key)


def get_file_url_from_public_s3(s3_key: str, expiration: int = 3600) -> str:
    """Получает URL для доступа к файлу через публичное API"""
    return public_s3_manager.get_file_url(s3_key, expiration)


def file_exists_in_public_s3(s3_key: str) -> bool:
    """Проверяет существование файла в S3 через публичное API"""
    return public_s3_manager.file_exists(s3_key)


def get_file_info_from_public_s3(s3_key: str) -> Dict[str, Any]:
    """Получает информацию о файле в S3 через публичное API"""
    return public_s3_manager.get_file_info(s3_key)


def list_files_in_public_s3(prefix: str = "", max_keys: int = 1000) -> Dict[str, Any]:
    """Получает список файлов в S3 через публичное API"""
    return public_s3_manager.list_files(prefix, max_keys)


def get_bucket_size_from_public_s3(prefix: str = "") -> Dict[str, Any]:
    """Получает общий размер файлов в бакете через публичное API"""
    return public_s3_manager.get_bucket_size(prefix) 