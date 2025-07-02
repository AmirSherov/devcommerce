import time
import logging
from typing import Dict, Any, List
from .services import AIGenerationService
from .image_service import pexels_service

logger = logging.getLogger(__name__)


class PremiumSmartAIGenerator:
    """
    🚀 ОПТИМИЗИРОВАННЫЙ AI ГЕНЕРАТОР ПОРТФОЛИО
    
    Создает профессиональные портфолио одним мощным запросом к AI
    с использованием всех данных пользователя
    """
    
    def __init__(self):
        self.ai_service = AIGenerationService()
        self.image_service = pexels_service
        logger.info("🎯 [OPTIMIZED AI] Инициализация оптимизированного генератора")

    def generate_portfolio_optimized(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        🚀 ОПТИМИЗИРОВАННАЯ ГЕНЕРАЦИЯ ПОРТФОЛИО - ОДИН ЗАПРОС К AI!
        
        Создает профессиональное портфолио одним мощным запросом со всеми данными пользователя
        """
        logger.info(f"🎯 [OPTIMIZED AI] Запуск оптимизированной генерации для: {request_data.get('title', 'Unknown')}")
        
        try:
            start_time = time.time()
            
            # Анализируем контекст пользователя
            context = self._analyze_project_context(request_data)
            logger.info(f"📊 [OPTIMIZED] Контекст: {context['profession']} / {context['design_style']}")
            
            # Создаем мега-промпт со всеми данными
            mega_prompt = self._build_optimized_prompt(context, request_data)
            logger.info(f"📝 [OPTIMIZED] Промпт создан, длина: {len(mega_prompt)} символов")
            
            # Делаем ОДИН запрос к AI
            try:
                ai_response = self.ai_service.call_openai_api(mega_prompt)
                logger.info("✅ [OPTIMIZED] AI ответил успешно")
            except Exception as e:
                logger.error(f"❌ [OPTIMIZED] Ошибка AI запроса: {str(e)}")
                raise Exception(f"Ошибка обращения к AI: {str(e)}")
            
            # Парсим ответ
            try:
                code_data = self.ai_service.parse_ai_response(ai_response)
                logger.info("✅ [OPTIMIZED] Код распарсен успешно")
            except Exception as e:
                logger.error(f"❌ [OPTIMIZED] Ошибка парсинга: {str(e)}")
                raise Exception(f"Ошибка обработки ответа AI: {str(e)}")
            
            # Интегрируем изображения
            try:
                enhanced_code = self._integrate_images_into_code(code_data, context)
                logger.info("🖼️ [OPTIMIZED] Изображения интегрированы")
            except Exception as e:
                logger.warning(f"⚠️ [OPTIMIZED] Ошибка изображений: {str(e)}")
                enhanced_code = code_data  # Используем код без изображений
            
            # Создаем портфолио
            try:
                portfolio = self.ai_service.create_portfolio_from_ai(enhanced_code, request_data)
                logger.info(f"🎉 [OPTIMIZED] Портфолио создано: {portfolio.slug}")
            except Exception as e:
                logger.error(f"❌ [OPTIMIZED] Ошибка создания портфолио: {str(e)}")
                raise Exception(f"Ошибка создания портфолио: {str(e)}")
            
            end_time = time.time()
            response_time = round(end_time - start_time, 2)
            
            logger.info(f"🚀 [OPTIMIZED] ✅ Генерация завершена за {response_time}с")
            
            return {
                'success': True,
                'portfolio': portfolio,
                'response_time': response_time,
                'generation_type': 'optimized_single_request',
                'enhanced_features': [
                    '🎯 Персональный анализ',
                    '🖼️ Автоматические изображения', 
                    '🎨 Уникальный дизайн',
                    '📱 Адаптивная верстка',
                    '⚡ Быстрая генерация'
                ]
            }
            
        except Exception as e:
            logger.error(f"💥 [OPTIMIZED] Критическая ошибка: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'error_code': 'OPTIMIZED_ERROR'
            }

    def _analyze_project_context(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """🔍 Анализ контекста персонального портфолио"""
        
        personal_info = request_data.get('personal_info', {})
        education = request_data.get('education', {})
        experience = request_data.get('experience', [])
        skills = request_data.get('skills', {})
        projects = request_data.get('projects', [])
        contacts = request_data.get('contacts', {})
        design_prefs = request_data.get('design_preferences', {})
        
        # 🖼️ ПОЛУЧАЕМ ИЗОБРАЖЕНИЯ ПОЛЬЗОВАТЕЛЯ
        profile_photo_data = request_data.get('profile_photo_data')
        diploma_image_url = request_data.get('diploma_image_url')
        
        # Извлекаем URL из profile_photo_data
        user_profile_photo = None
        if profile_photo_data and isinstance(profile_photo_data, dict):
            user_profile_photo = profile_photo_data.get('url')
        
        logger.info(f"🖼️ [CONTEXT] Profile photo URL: {user_profile_photo}")
        logger.info(f"🖼️ [CONTEXT] Diploma image URL: {diploma_image_url}")
        
        # Формируем профессиональный профиль
        full_name = f"{personal_info.get('firstName', '')} {personal_info.get('lastName', '')}"
        profession = personal_info.get('profession', 'Specialist')
        
        # Определяем индустрию на основе профессии
        industry_map = {
            'frontend': 'technology',
            'backend': 'technology', 
            'fullstack': 'technology',
            'mobile': 'technology',
            'designer': 'creative',
            'devops': 'technology',
            'qa': 'technology',
            'pm': 'business',
            'analyst': 'business'
        }
        industry = industry_map.get(profession.lower(), 'technology')
        
        # Создаем описательный промпт на основе данных пользователя
        bio_text = personal_info.get('bio', f"Профессиональный {profession}")
        tech_skills_text = ', '.join(skills.get('technical', ['программирование'])[:5])
        
        generated_prompt = f"Создать портфолио для {profession} {full_name}. {bio_text}. Основные навыки: {tech_skills_text}."
        
        # Определяем ключевые навыки для изображений
        tech_skills = skills.get('technical', [])
        image_keywords = self._extract_portfolio_image_keywords(profession, tech_skills)
        
        return {
            'portfolio_type': 'personal',
            'industry': industry,
            'style': design_prefs.get('style', 'modern'),
            'prompt': generated_prompt,
            'full_name': full_name,
            'profession': profession,
            'bio': personal_info.get('bio', ''),
            'location': personal_info.get('location', ''),
            'education': education,
            'experience': experience,
            'skills': skills,
            'projects': projects,
            'contacts': contacts,
            'design_style': design_prefs.get('style', 'modern'),
            'color_scheme': design_prefs.get('colorScheme', 'professional'),
            'theme': design_prefs.get('theme', 'clean'),
            'image_keywords': image_keywords,
            'primary_focus': self._detect_career_focus(profession, experience),
            'unique_strengths': self._extract_unique_strengths(experience, skills, projects),
            # 🖼️ ДОБАВЛЯЕМ ССЫЛКИ НА ИЗОБРАЖЕНИЯ ПОЛЬЗОВАТЕЛЯ
            'user_profile_photo': user_profile_photo,
            'user_diploma_image': diploma_image_url,
            'profile_photo_data': profile_photo_data  # Полные данные включая AI анализ
        }

    def _build_optimized_prompt(self, context: Dict, request_data: Dict) -> str:
        """
        📝 Создание мега-промпта со всеми данными пользователя
        """
        personal_info = request_data.get('personal_info', {})
        education = request_data.get('education', {})
        experience = request_data.get('experience', [])
        skills = request_data.get('skills', {})
        projects = request_data.get('projects', [])
        contacts = request_data.get('contacts', {})
        design_prefs = request_data.get('design_preferences', {})
        
        # Формируем описание опыта
        experience_text = ""
        for exp in experience[:3]:  # Берем первые 3 места работы
            experience_text += f"• {exp.get('position', 'Позиция')} в {exp.get('company', 'Компания')} - {exp.get('description', 'описание работы')}\n"
        
        # Формируем описание проектов
        projects_text = ""
        for proj in projects[:4]:  # Берем первые 4 проекта
            technologies = ', '.join(proj.get('technologies', []))
            projects_text += f"• {proj.get('name', 'Проект')}: {proj.get('description', 'описание')} (Технологии: {technologies})\n"
        
        # Формируем навыки
        tech_skills = ', '.join(skills.get('technical', []))
        soft_skills = ', '.join(skills.get('soft', []))
        
        return f"""Ты - SENIOR FRONTEND разработчик из Apple/Google с 10+ лет опыта. Создай ШЕДЕВР портфолио уровня Dribbble/Awwwards!

🎯 ПЕРСОНАЛЬНЫЕ ДАННЫЕ:
Имя: {personal_info.get('firstName', '')} {personal_info.get('lastName', '')}
Профессия: {personal_info.get('profession', 'Специалист')}
Локация: {personal_info.get('location', '')}
О себе: {personal_info.get('bio', '')}
Email: {contacts.get('email', '')}
Телефон: {contacts.get('phone', '')}
LinkedIn: {contacts.get('linkedin', '')}
GitHub: {contacts.get('github', '')}

🎓 ОБРАЗОВАНИЕ:
Учебное заведение: {education.get('university', 'Не указано')}
Степень: {education.get('degree', 'Не указано')}
Специальность: {education.get('field', 'Не указано')}
Год окончания: {education.get('graduationYear', 'Не указано')}

💼 ОПЫТ РАБОТЫ:
{experience_text}

🛠️ НАВЫКИ:
Технические: {tech_skills}
Личные качества: {soft_skills}

🚀 ПРОЕКТЫ:
{projects_text}

🎨 ДИЗАЙН ПРЕДПОЧТЕНИЯ:
Стиль: {design_prefs.get('style', 'modern')}
Цветовая схема: {design_prefs.get('colorScheme', 'professional')}
Тема: {design_prefs.get('theme', 'clean')}

🔥 ТРЕБОВАНИЯ К ДИЗАЙНУ 2024 (ОБЯЗАТЕЛЬНО!):

1. **HERO SECTION** - создай WOW эффект:
   - Полноэкранная высота (100vh)
   - Animated gradient background
   - Typing animation для имени
   - Floating particles background (CSS/JS)
   - Scroll indicator стрелка
   - Современная типографика (font-size: clamp())

2. **ЦВЕТОВАЯ СХЕМА** - современная палитра:
   :root {{
     --primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
     --accent: #00d4aa;
     --dark: #0f0f23;
     --text: #e2e8f0;
     --muted: #64748b;
     --glass: rgba(255, 255, 255, 0.1);
   }}

3. **СОВРЕМЕННЫЕ ЭФФЕКТЫ**:
   - Glassmorphism карточки (backdrop-filter: blur(10px))
   - Smooth parallax scrolling
   - Hover эффекты с transform: scale(1.05)
   - Box-shadow с цветными тенями
   - CSS animations (fadeInUp, slideIn)

4. **НАВЫКИ** - интерактивная визуализация:
   - Animated progress bars
   - Skill cards с hover 3D эффектами
   - Icon для каждого навыка
   - Percentage indicators


5. **ТИПОГРАФИКА**:
   - Google Fonts: 'Inter' для текста, 'Space Grotesk' для заголовков
   - Font weights: 300, 400, 500, 700
   - Line-height: 1.6 для читаемости

6. **АНИМАЦИИ (CSS + JS)**:
   ```css
   @keyframes fadeInUp {{
     from {{ opacity: 0; transform: translateY(30px); }}
     to {{ opacity: 1; transform: translateY(0); }}
   }}
   
   @keyframes typing {{
     from {{ width: 0; }}
     to {{ width: 100%; }}
   }}
   ```

8. **RESPONSIVE DESIGN**:
   - Mobile-first подход
   - Flexible containers
   - Adaptive font sizes (clamp())

9. **ИНТЕРАКТИВНОСТЬ**:
   - Smooth scroll behavior
   - Active section highlighting
   - Contact form с валидацией
   - Loader animation

🎨 ЦВЕТОВАЯ ПАЛИТРА (ИСПОЛЬЗУЙ ТОЧНО):
- Background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%)
- Primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%)
- Accent: #00d4aa
- Text: #e2e8f0
- Muted: #64748b

🏗️ СТРУКТУРА (ДЕТАЛЬНО):

1. **HERO** (100vh):
   - Animated background particles
   - Centered content с typing animation
   - CTA кнопки с hover эффектами
   - Scroll indicator

2. **ABOUT** (padding: 100px 0):
   - Two-column layout
   - Profile image с border-radius и shadow
   - Animated text appearance on scroll

3. **SKILLS** (dark section):
   - Grid layout навыков
   - Progress bars с animation
   - Icon + название + процент

4. **EXPERIENCE** (если есть):
   - Timeline design
   - Cards с company info
   - Hover эффекты
4. **CONTACT** (gradient background):
   - Centered form
   - Input стилизация
   - Social links с icons

🖼️ ИЗОБРАЖЕНИЯ:
- <img src="imageplace-userlogo" alt="Profile Photo" style="border-radius: 50%; width: 200px; height: 200px; object-fit: cover;">
- <img src="imageplace-project,portfolio,{personal_info.get('profession', 'developer')}" alt="Project">

📱 MOBILE RESPONSIVE:
```css
@media (max-width: 768px) {{
  .hero h1 {{ font-size: 2rem; }}
  .grid {{ grid-template-columns: 1fr; }}
  .container {{ padding: 0 20px; }}
}}
```

⚡ JAVASCRIPT ФИЧИ:
- Smooth scrolling
- Typing animation
- Progress bars animation on scroll
- Parallax эффекты
- Form validation

🚨 ВАЖНО! НЕ СОЗДАВАЙ ПРОСТЫЕ БЛОКИ ЦВЕТОВ! 
Создай ПРОФЕССИОНАЛЬНЫЙ дизайн с современными градиентами, анимациями и эффектами!

🔥 ОБЯЗАТЕЛЬНЫЕ СЕКЦИИ:

1. **HERO** - полноэкранный с анимированным фоном и typing эффектом имени
2. **ABOUT** - две колонки с фото профиля и описанием  
3. **SKILLS** - интерактивные прогресс бары с процентами
4. **CONTACT** - стильная форма с градиентным фоном

🎨 ОБЯЗАТЕЛЬНО ДОБАВЬ ОТ СЕБЯ:
- Темный градиентный фон
- Glassmorphism карточки (backdrop-filter: blur)
- Плавающие частицы на фоне
- Typing animation для имени
- Smooth scroll между секциями
- Интерактивные hover эффекты
- Прогресс индикатор прокрутки
- Parallax эффекты
- Современные градиенты и анимации

⚡ JAVASCRIPT ФИЧИ:
- Анимация навыков при скролле
- Typing эффект
- Smooth scroll navigation
- Progress bar для скролла

🚨 НЕ СОЗДАВАЙ ПРОСТЫЕ СТИЛИ! ИСПОЛЬЗУЙ ВСЕ СОВРЕМЕННЫЕ CSS ФИШКИ 2024!

ОТВЕЧАЙ СТРОГО JSON:
{{"html": "ПОЛНЫЙ СОВРЕМЕННЫЙ HTML", "css": "ПОЛНЫЙ CSS С АНИМАЦИЯМИ", "js": "ПОЛНЫЙ JS С ИНТЕРАКТИВНОСТЬЮ"}}

СОЗДАЙ ПОРТФОЛИО УРОВНЯ APPLE/GOOGLE! БЕЗ КОМПРОМИССОВ! 🚀✨"""

    def _integrate_images_into_code(self, code_data: Dict, context: Dict) -> Dict[str, str]:
        """🖼️ Автоматическая интеграция изображений в код"""
        
        try:
            html_code = code_data.get('html', '')
            css_code = code_data.get('css', '')
            
            # 1. ЗАМЕНЯЕМ ПЛЕЙСХОЛДЕРЫ НА РЕАЛЬНЫЕ ССЫЛКИ ПОЛЬЗОВАТЕЛЯ
            html_code = self._replace_user_image_placeholders(html_code, context)
            
            # 2. Добавляем hero background изображение
            hero_image = self._get_hero_image(context)
            if hero_image:
                css_code = self._inject_hero_image_css(css_code, hero_image)
                logger.info(f"🖼️ [BACKGROUND] Hero background добавлен: {hero_image[:50]}...")
            
            # 3. Добавляем section background изображения
            section_images = self._get_section_images(context)
            if section_images:
                css_code = self._inject_section_images_css(css_code, section_images)
                logger.info(f"🖼️ [BACKGROUND] Добавлено {len(section_images)} background изображений")
            
            return {
                'html': html_code,
                'css': css_code,
                'js': code_data.get('js', '')
            }
            
        except Exception as e:
            logger.error(f"❌ [IMAGES] Ошибка интеграции изображений: {str(e)}")
            # Возвращаем код без дополнительных изображений
            return code_data

    def _replace_user_image_placeholders(self, html_code: str, context: Dict) -> str:
        """🔄 Замена плейсхолдеров на реальные ссылки пользователя"""
        try:
            # Получаем ссылки на загруженные изображения пользователя
            user_profile_photo = context.get('user_profile_photo')  # Ссылка на фото профиля
            user_diploma_image = context.get('user_diploma_image')  # Ссылка на диплом
            
            logger.info(f"🔄 [PLACEHOLDERS] Profile photo: {user_profile_photo}")
            logger.info(f"🔄 [PLACEHOLDERS] Diploma image: {user_diploma_image}")
            
            # Заменяем плейсхолдер фото профиля
            if user_profile_photo:
                html_code = html_code.replace('src="imageplace-userlogo"', f'src="{user_profile_photo}"')
                html_code = html_code.replace("src='imageplace-userlogo'", f"src='{user_profile_photo}'")
                logger.info("✅ [PLACEHOLDERS] Заменен плейсхолдер imageplace-userlogo")
            else:
                # Если нет фото пользователя, используем профессиональный аватар
                default_avatar = f"https://ui-avatars.com/api/?name={context.get('full_name', 'User')}&size=300&background=667eea&color=ffffff&bold=true"
                html_code = html_code.replace('src="imageplace-userlogo"', f'src="{default_avatar}"')
                html_code = html_code.replace("src='imageplace-userlogo'", f"src='{default_avatar}'")
                logger.info("⚠️ [PLACEHOLDERS] Использован дефолтный аватар")
            
            # Заменяем плейсхолдер диплома
            if user_diploma_image:
                html_code = html_code.replace('src="imageplace-diploma"', f'src="{user_diploma_image}"')
                html_code = html_code.replace("src='imageplace-diploma'", f"src='{user_diploma_image}'")
                logger.info("✅ [PLACEHOLDERS] Заменен плейсхолдер imageplace-diploma")
            else:
                # Если нет диплома, удаляем img теги для диплома
                import re
                html_code = re.sub(r'<img[^>]*src="imageplace-diploma"[^>]*>', '', html_code)
                html_code = re.sub(r"<img[^>]*src='imageplace-diploma'[^>]*>", '', html_code)
                logger.info("⚠️ [PLACEHOLDERS] Удалены img теги для диплома (не загружен)")
            
            return html_code
            
        except Exception as e:
            logger.error(f"❌ [PLACEHOLDERS] Ошибка замены плейсхолдеров: {str(e)}")
            return html_code

    def _get_hero_image(self, context: Dict) -> str:
        """Получение главного изображения"""
        try:
            profession = context.get('profession', 'professional')
            search_query = f"{profession} professional modern workspace"
            
            images = self.image_service.search_images(
                query=search_query,
                component_type='hero',
                count=1
            )
            
            return images[0] if images else None
            
        except Exception as e:
            logger.error(f"❌ Hero image error: {str(e)}")
            return None

    def _get_section_images(self, context: Dict) -> List[str]:
        """Получение изображений для секций"""
        try:
            section_images = []
            profession = context.get('profession', 'professional')
            
            # Получаем 3 изображения для секций
            for section_type in ['skills', 'projects', 'contact']:
                search_query = f"{profession} {section_type} technology workspace"
                
                images = self.image_service.search_images(
                    query=search_query,
                    component_type='features',
                    count=1
                )
                
                if images:
                    section_images.extend(images)
            
            return section_images
            
        except Exception as e:
            logger.error(f"❌ Section images error: {str(e)}")
            return []

    def _inject_hero_image_css(self, css_code: str, image_url: str) -> str:
        """Добавление hero изображения в CSS"""
        hero_css = f"""
/* AI Generated Hero Background */
.hero, .hero-section, section:first-of-type, .banner, .intro {{
    background-image: linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('{image_url}');
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}
"""
        return css_code + hero_css

    def _inject_section_images_css(self, css_code: str, images: List[str]) -> str:
        """Добавление изображений секций в CSS"""
        section_css = ""
        
        for i, image_url in enumerate(images):
            section_css += f"""
/* AI Generated Section Image {i+1} */
.section-{i+1}, .feature-{i+1}, .service-{i+1} {{
    background-image: url('{image_url}');
    background-size: cover;
    background-position: center;
}}
"""
        
        return css_code + section_css

    def _extract_portfolio_image_keywords(self, profession: str, tech_skills: List[str]) -> List[str]:
        """Извлечение ключевых слов для изображений портфолио"""
        profession_keywords = {
            'frontend': ['frontend', 'web development', 'ui design', 'javascript', 'react'],
            'backend': ['backend', 'server', 'database', 'api', 'programming'],
            'fullstack': ['fullstack', 'web development', 'programming', 'technology', 'coding'],
            'mobile': ['mobile', 'app development', 'smartphone', 'android', 'ios'],
            'designer': ['ui design', 'ux design', 'design', 'creative', 'interface'],
            'devops': ['devops', 'cloud', 'infrastructure', 'deployment', 'automation'],
            'qa': ['testing', 'quality assurance', 'bug testing', 'software testing'],
            'pm': ['project management', 'team', 'planning', 'agile', 'leadership'],
            'analyst': ['data analysis', 'analytics', 'charts', 'business intelligence']
        }
        
        base_keywords = profession_keywords.get(profession.lower(), ['programming', 'technology', 'professional'])
        
        # Добавляем технические навыки как ключевые слова
        tech_keywords = [skill.lower() for skill in tech_skills[:3]]  # Первые 3 навыка
        
        return base_keywords + tech_keywords + ['professional', 'modern', 'workspace']
    
    def _detect_career_focus(self, profession: str, experience: List[Dict]) -> str:
        """Определение карьерного фокуса"""
        if not experience:
            return f"Начинающий {profession}"
            
        companies = [exp.get('company', '') for exp in experience]
        
        # Анализируем типы компаний
        startup_indicators = ['startup', 'стартап', 'новая компания']
        corporate_indicators = ['corporation', 'корпорация', 'большая компания', 'enterprise']
        
        startup_count = sum(1 for company in companies if any(ind in company.lower() for ind in startup_indicators))
        corporate_count = sum(1 for company in companies if any(ind in company.lower() for ind in corporate_indicators))
        
        if startup_count > corporate_count:
            return f"{profession} с опытом в стартапах"
        elif corporate_count > startup_count:
            return f"{profession} с корпоративным опытом"
        else:
            return f"Универсальный {profession}"
    
    def _extract_unique_strengths(self, experience: List[Dict], skills: Dict, projects: List[Dict]) -> List[str]:
        """Извлечение уникальных сильных сторон"""
        strengths = []
        
        # Анализ опыта
        if len(experience) >= 3:
            strengths.append("Богатый опыт в различных компаниях")
        
        # Анализ навыков
        technical_skills = skills.get('technical', [])
        if len(technical_skills) >= 5:
            strengths.append("Широкий технический стек")
        
        # Анализ проектов
        if len(projects) >= 3:
            strengths.append("Портфолио разнообразных проектов")
        
        # Анализ технологий в проектах
        all_technologies = []
        for project in projects:
            all_technologies.extend(project.get('technologies', []))
        
        unique_technologies = list(set(all_technologies))
        if len(unique_technologies) >= 8:
            strengths.append("Опыт с множеством технологий")
            
        return strengths if strengths else ["Мотивированный специалист", "Готовность к новым вызовам"]

    # Совместимость со старым интерфейсом
    def generate_website(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Точка входа - теперь использует оптимизированную генерацию"""
        return self.generate_portfolio_optimized(request_data)


# Обновляем основной класс для обратной совместимости
SmartAIGenerator = PremiumSmartAIGenerator 