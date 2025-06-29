"""
Тестовый скрипт для проверки работы Pexels API
Запустите: python pexels_test.py

Документация: https://www.pexels.com/api/documentation
"""

import os
import sys
import django
from pathlib import Path

# Добавляем родительскую директорию в PYTHONPATH
sys.path.append(str(Path(__file__).parent.parent))

# Настраиваем Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'devcommercebackend.settings')
django.setup()

import requests
import logging
from pprint import pprint

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_pexels_api():
    """Тестирование Pexels API"""
    
    # API ключ из скриншота (без пробелов и переносов строк)
    api_key = "6r96KapNJVJkZ9Y22Bfa6dSiYYqPuvd0bbYQIhzTpmjyNhRtOGGcB6nj".strip()
    logger.info(f"Используем API ключ: {api_key[:10]}...")
    
    # Базовый URL для Pexels API
    base_url = "https://api.pexels.com/v1"
    
    # Заголовки для запроса (согласно документации)
    headers = {
        "Authorization": api_key.strip(),  # Убеждаемся, что нет лишних пробелов
    }
    
    # Простой тестовый запрос
    try:
        # Сначала проверим статус API
        logger.info("\nПроверяем статус API...")
        response = requests.get(
            "https://api.pexels.com/v1/search",
            headers=headers,
            params={"query": "test", "per_page": 1}
        )
        
        logger.info(f"Статус код: {response.status_code}")
        logger.info(f"Заголовки ответа: {dict(response.headers)}")
        logger.info(f"Тело ответа: {response.text}")
        
        if response.status_code == 401:
            logger.error("❌ Ошибка аутентификации. Проверьте API ключ.")
            logger.info("Текущий ключ:")
            logger.info(f"Длина: {len(api_key)}")
            logger.info(f"Значение: '{api_key}'")
            logger.info(f"Заголовок Authorization: '{headers['Authorization']}'")
            return
            
        # Если статус ок, продолжаем с поиском
        if response.status_code == 200:
            logger.info("\nAPI работает! Пробуем поиск изображений...")
            search_response = requests.get(
                f"{base_url}/search",
                headers=headers,
                params={"query": "modern office", "per_page": 1}
            )
            
            if search_response.status_code == 200:
                data = search_response.json()
                logger.info(f"✅ Успех! Найдено фото: {data['total_results']}")
                if data['photos']:
                    photo = data['photos'][0]
                    logger.info(f"Первое фото:")
                    logger.info(f"- ID: {photo['id']}")
                    logger.info(f"- URL: {photo['url']}")
            else:
                logger.error(f"❌ Ошибка поиска: {search_response.status_code}")
                logger.error(search_response.text)
                
    except Exception as e:
        logger.error(f"❌ Ошибка при запросе: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    logger.info("🚀 Начинаем тестирование Pexels API...")
    test_pexels_api()
    logger.info("✨ Тестирование завершено!") 