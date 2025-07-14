const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

/**
 * 🤖 API ДЛЯ РАБОТЫ С AI ЗАПОЛНЕНИЕМ ШАБЛОНОВ
 */

import { getSessionHeaders } from '@/lib/auth-utils';

class AIAPI {
    constructor() {
        this.baseURL = `${API_BASE_URL}/ai`;
    }

    /**
     * Получение токена авторизации
     */
    getAuthHeaders() {
        const token = localStorage.getItem('access_token');
        return token ? {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
        } : {
            'Content-Type': 'application/json',
        };
    }

    /**
     * 🤖 AI заполнение шаблона
     */
    async generateTemplate(templateId, aiData) {
        try {
            const response = await fetch(`${this.baseURL}/templates/${templateId}/generate/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...getSessionHeaders(),
                },
                body: JSON.stringify({
                    project_title: aiData.projectTitle,
                    project_description: aiData.projectDescription,
                    user_data: aiData.userData,
                }),
            });

            const data = await response.json()

            return data;
        } catch (error) {
            console.error('Ошибка AI генерации:', error);
            throw error;
        }
    }

    /**
     * 🔒 Получение лимитов AI генераций пользователя
     */
    async getUserLimits() {
        try {
            const response = await fetch(`${this.baseURL}/limits/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...getSessionHeaders(),
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения лимитов:', error);
            throw error;
        }
    }

    /**
     * 📊 Получение статистики AI использования
     */
    async getAIStats() {
        try {
            const response = await fetch(`${this.baseURL}/stats/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...getSessionHeaders(),
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения статистики AI:', error);
            throw error;
        }
    }

    /**
     * 📝 Получение истории AI генераций
     */
    async getAIHistory(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            if (params.page) queryParams.append('page', params.page);
            if (params.page_size) queryParams.append('page_size', params.page_size);

            const url = `${this.baseURL}/history/?${queryParams.toString()}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...getSessionHeaders(),
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения истории AI:', error);
            throw error;
        }
    }

    /**
     * 📈 Учет обычного использования шаблона
     */
    async trackRegularUsage(templateId) {
        try {
            const response = await fetch(`${this.baseURL}/track-regular-usage/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...this.getAuthHeaders(),
                    ...getSessionHeaders(),
                },
                body: JSON.stringify({
                    template_id: templateId,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Ошибка учета использования');
            }

            return data;
        } catch (error) {
            console.error('Ошибка учета использования:', error);
            throw error;
        }
    }
}

// Создаем и экспортируем экземпляр API
export const aiAPI = new AIAPI();

// Утилиты для работы с ошибками
export const getAIErrorMessage = (error) => {
    switch (error.code) {
        case 'PREMIUM_REQUIRED':
            return 'AI генерация доступна только Premium пользователям';
        case 'DAILY_LIMIT_EXCEEDED':
            return 'Превышен дневной лимит AI генераций';
        case 'TEMPLATE_NOT_FOUND':
            return 'Шаблон не найден';
        case 'AI_SERVICE_ERROR':
            return 'Ошибка сервиса AI. Попробуйте позже';
        case 'VALIDATION_ERROR':
            return 'Проверьте правильность введенных данных';
        default:
            return error.message || 'Произошла ошибка при AI генерации';
    }
};

// Константы
export const AI_STATUS = {
    'pending': 'Ожидает',
    'processing': 'Обрабатывается',
    'completed': 'Завершено',
    'failed': 'Ошибка'
};

export const DEFAULT_USER_DATA_PLACEHOLDER = `Пример заполнения:

ПЕРСОНАЛЬНАЯ ИНФОРМАЦИЯ:
- Имя: Иван Петров
- Специализация: Frontend разработчик
- Опыт: 3 года
- Местоположение: Москва

ОБРАЗОВАНИЕ:
- Университет: МГУ
- Специальность: Информатика
- Год окончания: 2020

НАВЫКИ:
- JavaScript, React, Vue.js
- HTML5, CSS3, SASS
- Git, Webpack, Node.js
- Figma, Adobe XD

ОПЫТ РАБОТЫ:
- Frontend Developer в TechCorp (2021-2024)
- Junior Developer в StartupXYZ (2020-2021)

ПРОЕКТЫ:
- Интернет-магазин на React
- Корпоративный сайт с CMS
- Мобильное приложение на React Native

КОНТАКТЫ:
- Email: ivan@example.com
- GitHub: github.com/ivan
- LinkedIn: linkedin.com/in/ivan
- Телефон: +7 999 123-45-67`; 