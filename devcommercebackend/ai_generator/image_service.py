import requests
import time
import logging
import random
from typing import List, Dict, Optional
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)


class PexelsImageService:
    """Сервис для работы с Pexels API"""
    
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
                'https://images.pexels.com/photos/3184339/pexels-photo-3184339.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
            ],
            'features': [
                'https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop',
                'https://images.pexels.com/photos/3184398/pexels-photo-3184398.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop',
                'https://images.pexels.com/photos/3184433/pexels-photo-3184433.jpeg?auto=compress&cs=tinysrgb&w=400&h=300&fit=crop',
            ],
            'gallery': [
                'https://images.pexels.com/photos/3184360/pexels-photo-3184360.jpeg?auto=compress&cs=tinysrgb&w=500&h=400&fit=crop',
                'https://images.pexels.com/photos/3184465/pexels-photo-3184465.jpeg?auto=compress&cs=tinysrgb&w=500&h=400&fit=crop',
                'https://images.pexels.com/photos/3184339/pexels-photo-3184339.jpeg?auto=compress&cs=tinysrgb&w=500&h=400&fit=crop',
            ],
            'contact': [
                'https://images.pexels.com/photos/3184292/pexels-photo-3184292.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop',
                'https://images.pexels.com/photos/3184398/pexels-photo-3184398.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop',
                'https://images.pexels.com/photos/3184433/pexels-photo-3184433.jpeg?auto=compress&cs=tinysrgb&w=600&h=400&fit=crop',
            ],
            'restaurant': [
                'https://images.pexels.com/photos/262978/pexels-photo-262978.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
                'https://images.pexels.com/photos/67468/pexels-photo-67468.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
                'https://images.pexels.com/photos/941861/pexels-photo-941861.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
            ],
            'technology': [
                'https://images.pexels.com/photos/276452/pexels-photo-276452.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
                'https://images.pexels.com/photos/577585/pexels-photo-577585.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
                'https://images.pexels.com/photos/574071/pexels-photo-574071.jpeg?auto=compress&cs=tinysrgb&w=800&h=600&fit=crop',
            ],
        }
        
        if not self.enabled:
            logger.info("[PEXELS] Сервис отключен, используются fallback изображения")
    
    def _rate_limit_delay(self):
        """Соблюдение лимитов API"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
    
    def _get_cache_key(self, query: str, orientation: str, per_page: int) -> str:
        """Генерация ключа кэша для изображений"""
        return f"pexels_images_{query}_{orientation}_{per_page}"
    
    def search_images(self, query: str, component_type: str = 'general', count: int = 1) -> List[str]:
        """
        Поиск изображений на Pexels или возврат fallback изображений
        
        Args:
            query: Поисковый запрос
            component_type: Тип компонента (hero, features, gallery, contact)
            count: Количество изображений
        
        Returns:
            Список URL изображений
        """
        if not self.enabled:
            return self._get_fallback_images(component_type, count)
        
        try:
            return self._search_pexels(query, count)
        except Exception as e:
            logger.error(f"[PEXELS ERROR] Ошибка поиска: {e}")
            return self._get_fallback_images(component_type, count)

    def _search_pexels(self, query: str, count: int = 1) -> List[str]:
        """Поиск изображений через Pexels API"""
        if not self.access_key:
            raise ValueError("Pexels Access Key не настроен")
        self._rate_limit_delay()
        headers = {
            "Authorization": self.access_key
        }
        
        search_url = f"{self.base_url}/search"
        params = {
            'query': query,
            'per_page': min(count, 80),  
            'orientation': 'landscape',
            'size': 'large'  
        }
        
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=15)
            if response.status_code == 200:
                data = response.json()
                photos = data.get('photos', [])
                
                if not photos:
                    logger.warning(f"[PEXELS] Нет результатов для запроса: {query}")
                    return []
                
                images = []
                for photo in photos[:count]:
                    image_url = photo.get('src', {}).get('large')
                    if image_url:
                        images.append(image_url)
                        logger.info(f"[PEXELS] Найдено изображение: {photo.get('id')} - {photo.get('url')}")
                
                logger.info(f"[PEXELS API] Успешно получено {len(images)} изображений")
                return images
            else:
                error_text = response.text
                logger.error(f"[PEXELS ERROR] {response.status_code}: {error_text}")
                raise Exception(f"HTTP {response.status_code}: {error_text}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"[PEXELS ERROR] Ошибка запроса: {str(e)}")
            raise Exception(f"Ошибка запроса к Pexels API: {str(e)}")

    def _get_fallback_images(self, component_type: str, count: int) -> List[str]:
        """Получение fallback изображений"""
        category = component_type
        if component_type not in self.fallback_images:
            if 'restaurant' in component_type.lower() or 'food' in component_type.lower():
                category = 'restaurant'
            elif 'tech' in component_type.lower() or 'IT' in component_type.lower():
                category = 'technology'
            else:
                category = 'hero'  
        
        available_images = self.fallback_images.get(category, self.fallback_images['hero'])
        if count <= len(available_images):
            selected = random.sample(available_images, count)
        else:
            selected = available_images * (count // len(available_images) + 1)
            selected = selected[:count]
        
        logger.info(f"[FALLBACK] Возвращено {len(selected)} fallback изображений категории '{category}'")
        return selected

    def get_industry_keywords(self, industry: str) -> List[str]:
        """Получение ключевых слов для индустрии"""
        keywords_map = {
            'restaurant': ['restaurant', 'food', 'dining', 'chef', 'kitchen', 'meal'],
            'technology': ['technology', 'computer', 'software', 'coding', 'innovation'],
            'healthcare': ['healthcare', 'medical', 'hospital', 'doctor', 'health'],
            'fitness': ['fitness', 'gym', 'workout', 'exercise', 'sport'],
            'education': ['education', 'school', 'learning', 'student', 'classroom'],
            'business': ['business', 'office', 'meeting', 'corporate', 'professional'],
            'ecommerce': ['shopping', 'store', 'retail', 'commerce', 'product'],
            'travel': ['travel', 'vacation', 'destination', 'journey', 'adventure'],
        }
        
        return keywords_map.get(industry.lower(), ['business', 'professional', 'modern'])

    def get_images_for_component(
        self, 
        component_type: str, 
        industry: str, 
        count: int = 1,
        style: str = 'modern'
    ) -> List[str]:
        """
        Умный подбор изображений для конкретного типа компонента
        
        Args:
            component_type: Тип компонента (hero, gallery, etc.)
            industry: Индустрия (restaurant, tech, etc.)
            count: Количество изображений
            style: Стиль (modern, creative, etc.)
        
        Returns:
            Список подходящих изображений URL
        """
        smart_queries = {
            'hero': {
                'restaurant': ['restaurant interior elegant modern', 'fine dining atmosphere'],
                'tech': ['modern office startup workspace', 'technology innovation'],
                'health': ['modern medical clinic clean', 'healthcare professional'],
                'fitness': ['modern gym equipment fitness', 'healthy lifestyle'],
                'creative': ['creative workspace inspiration', 'artistic modern studio'],
                'business': ['modern office professional', 'business team meeting'],
                'education': ['modern classroom learning', 'students education'],
                'general': ['modern professional workspace', 'clean minimal design']
            },
            'gallery': {
                'restaurant': ['delicious food photography', 'gourmet dishes presentation'],
                'tech': ['modern devices technology', 'clean tech products'],
                'health': ['medical equipment modern', 'healthcare tools'],
                'fitness': ['fitness equipment gym', 'workout exercises'],
                'creative': ['creative work portfolio', 'artistic projects'],
                'business': ['business solutions', 'professional services'],
                'education': ['educational materials', 'learning resources'],
                'general': ['professional portfolio work', 'quality products']
            },
            'features': {
                'restaurant': ['restaurant service quality', 'dining experience'],
                'tech': ['technology features benefits', 'software interface'],
                'health': ['healthcare services', 'medical care'],
                'fitness': ['fitness benefits results', 'healthy transformation'],
                'creative': ['creative services design', 'artistic solutions'],
                'business': ['business growth success', 'professional results'],
                'education': ['learning outcomes success', 'educational progress'],
                'general': ['professional quality service', 'excellent results']
            },
            'contact': {
                'restaurant': ['restaurant contact welcome', 'friendly service'],
                'tech': ['tech support help', 'customer service'],
                'health': ['medical consultation', 'healthcare support'],
                'fitness': ['fitness consultation', 'personal trainer'],
                'creative': ['creative consultation', 'design meeting'],
                'business': ['business meeting contact', 'professional consultation'],
                'education': ['educational support help', 'learning assistance'],
                'general': ['customer support contact', 'professional help']
            }
        }
        queries = smart_queries.get(component_type, {}).get(
            industry, 
            smart_queries.get(component_type, {}).get('general', [f'{industry} professional'])
        )
        
        if not queries:
            queries = [f'{industry} {component_type} professional modern']
        selected_query = random.choice(queries)
        style_modifiers = {
            'modern': 'clean modern minimal',
            'creative': 'creative artistic unique',
            'business': 'professional corporate',
            'elegant': 'elegant sophisticated luxury',
            'playful': 'bright colorful fun',
            'dark': 'dark moody atmospheric'
        }
        
        if style in style_modifiers:
            selected_query += f' {style_modifiers[style]}'
        
        logger.info(f"[PEXELS] Поиск изображений: '{selected_query}' для {component_type}/{industry}")
        return self.search_images(
            query=selected_query,
            component_type=component_type,
            count=count
        )
    
    def get_multiple_component_images(self, components_data: List[Dict]) -> Dict[str, List[str]]:
        """
        Получение изображений для множества компонентов за один раз
        
        Args:
            components_data: Список данных компонентов
            
        Returns:
            Словарь с изображениями для каждого компонента
        """
        
        images_result = {}
        
        for component in components_data:
            component_id = component.get('id', '')
            component_type = component.get('type', '').split('_')[0]  
            industry = component.get('industry', 'general')
            style = component.get('style', 'modern')
            images_needed = 1
            if component_type == 'gallery':
                images_needed = component.get('props', {}).get('images_count', 6)
            elif component_type == 'features':
                images_needed = 3
            
            try:
                images = self.get_images_for_component(
                    component_type=component_type,
                    industry=industry,
                    count=images_needed,
                    style=style
                )
                
                images_result[component_id] = images
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"[PEXELS] Ошибка получения изображений для {component_id}: {str(e)}")
                images_result[component_id] = self._get_fallback_images(component_type, images_needed)
        
        return images_result
pexels_service = PexelsImageService() 