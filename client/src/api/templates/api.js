const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000';
    
/**
 * 🎨 API ДЛЯ РАБОТЫ С ШАБЛОНАМИ ПОРТФОЛИО
 */

class TemplatesAPI {
    constructor() {
        this.baseURL = `${API_BASE_URL}/templates`;
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
     * 📋 Получение списка шаблонов
     */
    async getTemplates(params = {}) {
        try {
            const queryParams = new URLSearchParams();
            
            // Добавляем параметры фильтрации
            if (params.category) queryParams.append('category', params.category);
            if (params.difficulty) queryParams.append('difficulty', params.difficulty);
            if (params.is_premium !== undefined) queryParams.append('is_premium', params.is_premium);
            if (params.featured) queryParams.append('featured', params.featured);
            if (params.search) queryParams.append('search', params.search);
            if (params.sort) queryParams.append('sort', params.sort);
            if (params.page) queryParams.append('page', params.page);
            if (params.page_size) queryParams.append('page_size', params.page_size);

            const url = `${this.baseURL}/?${queryParams.toString()}`;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения шаблонов:', error);
            throw error;
        }
    }

    /**
     * 📄 Получение детальной информации о шаблоне
     */
    async getTemplate(templateId) {
        try {
            const response = await fetch(`${this.baseURL}/${templateId}/`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения шаблона:', error);
            throw error;
        }
    }

    /**
     * 👁️ Получение URL превью шаблона
     */
    getPreviewUrl(template) {
        return template.demo_url;
    }

    /**
     * 🎯 Использование шаблона для создания портфолио
     */
    async useTemplate(templateId, portfolioData = {}) {
        try {
            const response = await fetch(`${this.baseURL}/use/`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
                body: JSON.stringify({
                    template_id: templateId,
                    portfolio_title: portfolioData.title,
                    portfolio_description: portfolioData.description,
                }),
            });

            const data = await response.json();

            if (!response.ok) {
                throw {
                    status: response.status,
                    message: data.error || 'Ошибка использования шаблона',
                    code: data.error_code,
                    details: data.details
                };
            }

            return data;
        } catch (error) {
            console.error('Ошибка использования шаблона:', error);
            throw error;
        }
    }

    /**
     * 👍 Лайкнуть шаблон
     */
    async likeTemplate(templateId) {
        try {
            const response = await fetch(`${this.baseURL}/${templateId}/like/`, {
                method: 'POST',
                headers: this.getAuthHeaders(),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Ошибка добавления лайка');
            }

            return data;
        } catch (error) {
            console.error('Ошибка лайка шаблона:', error);
            throw error;
        }
    }

    /**
     * 💔 Убрать лайк с шаблона
     */
    async unlikeTemplate(templateId) {
        try {
            const response = await fetch(`${this.baseURL}/${templateId}/like/`, {
                method: 'DELETE',
                headers: this.getAuthHeaders(),
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Ошибка удаления лайка');
            }

            return data;
        } catch (error) {
            console.error('Ошибка удаления лайка:', error);
            throw error;
        }
    }

    /**
     * 📈 Получение статистики шаблонов
     */
    async getStats() {
        try {
            const response = await fetch(`${this.baseURL}/stats/`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения статистики:', error);
            throw error;
        }
    }

    /**
     * 🏷️ Получение списка категорий
     */
    async getCategories() {
        try {
            const response = await fetch(`${this.baseURL}/categories/`, {
                method: 'GET',
                headers: this.getAuthHeaders(),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            return data;
        } catch (error) {
            console.error('Ошибка получения категорий:', error);
            throw error;
        }
    }
}

// Создаем и экспортируем экземпляр API
export const templatesAPI = new TemplatesAPI();

// Константы для удобства
export const TEMPLATE_DIFFICULTIES = {
    'beginner': 'Начинающий',
    'intermediate': 'Средний', 
    'advanced': 'Продвинутый'
};

export const TEMPLATE_SORT_OPTIONS = {
    'featured': 'Рекомендуемые',
    'popular': 'Популярные',
    'newest': 'Новые',
    'most_used': 'Часто используемые',
    'alphabetical': 'По алфавиту'
};

// Утилиты для работы с ошибками
export const getTemplateErrorMessage = (error) => {
    if (error.code === 'PREMIUM_REQUIRED') {
        return 'Этот шаблон доступен только Premium пользователям';
    }
    
    return error.message || 'Произошла ошибка при работе с шаблонами';
}; 