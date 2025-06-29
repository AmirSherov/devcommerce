import { getAuthHeaders } from '../../lib/auth-utils';
import { API_BASE_URL } from '../auth/api';

class AIAPIError extends Error {
  constructor(message, code, status) {
    super(message);
    this.code = code;
    this.status = status;
  }
}

export const aiAPI = {
  /**
   * Генерация портфолио через AI
   */
  async generatePortfolio(data) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new AIAPIError(
          result.error || 'Ошибка генерации',
          result.error_code || 'UNKNOWN',
          response.status
        );
      }

      return result;
    } catch (error) {
      if (error instanceof AIAPIError) {
        throw error;
      }
      throw new AIAPIError('Ошибка сети', 'NETWORK_ERROR', 0);
    }
  },

  /**
   * Получение лимитов пользователя
   */
  async getUserLimits() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/limits/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения лимитов');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI limits:', error);
      throw error;
    }
  },

  /**
   * Получение истории AI генераций
   */
  async getGenerationHistory(page = 1, pageSize = 20) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/ai/history/?page=${page}&page_size=${pageSize}`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка получения истории');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI history:', error);
      throw error;
    }
  },

  /**
   * Получение статистики пользователя
   */
  async getUserStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/stats/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения статистики');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI stats:', error);
      throw error;
    }
  },

  /**
   * Получение шаблонов промптов
   */
  async getPromptTemplates(category = null, style = null) {
    try {
      const params = new URLSearchParams();
      if (category) params.append('category', category);
      if (style) params.append('style', style);

      const response = await fetch(
        `${API_BASE_URL}/ai/templates/?${params.toString()}`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка получения шаблонов');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI templates:', error);
      throw error;
    }
  },

  /**
   * Сохранение промпта как шаблона
   */
  async savePromptTemplate(templateData) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/templates/save/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(templateData),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Ошибка сохранения шаблона');
      }

      return await response.json();
    } catch (error) {
      console.error('Error saving AI template:', error);
      throw error;
    }
  },

  /**
   * Удаление шаблона промпта
   */
  async deletePromptTemplate(templateId) {
    try {
      const response = await fetch(
        `${API_BASE_URL}/ai/templates/${templateId}/delete/`,
        {
          method: 'DELETE',
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Ошибка удаления шаблона');
      }

      return await response.json();
    } catch (error) {
      console.error('Error deleting AI template:', error);
      throw error;
    }
  },

  /**
   * 🚀 ПРЕМИУМ генерация сайта через революционный 7-шаговый AI
   */
  async premiumGenerate(data) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/premium-generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new AIAPIError(
          result.error || 'Ошибка премиум генерации',
          result.error_code || 'PREMIUM_ERROR',
          response.status
        );
      }

      return result;
    } catch (error) {
      if (error instanceof AIAPIError) {
        throw error;
      }
      throw new AIAPIError('Ошибка сети при премиум генерации', 'NETWORK_ERROR', 0);
    }
  },

  /**
   * Умная генерация сайта через новый AI (улучшенный)
   */
  async smartGenerate(data) {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/smart-generate/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new AIAPIError(
          result.error || 'Ошибка генерации',
          result.error_code || 'UNKNOWN',
          response.status
        );
      }

      return result;
    } catch (error) {
      if (error instanceof AIAPIError) {
        throw error;
      }
      throw new AIAPIError('Ошибка сети', 'NETWORK_ERROR', 0);
    }
  },

  /**
   * Получение метрик AI генерации
   */
  async getMetrics() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/metrics/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения метрик');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching AI metrics:', error);
      throw error;
    }
  },

  /**
   * Получение информации о кэше AI
   */
  async getCacheInfo() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/cache/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения информации о кэше');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching cache info:', error);
      throw error;
    }
  },

  /**
   * Очистка кэша AI (только для админов)
   */
  async clearCache() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/cache/clear/`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Ошибка очистки кэша');
      }

      return await response.json();
    } catch (error) {
      console.error('Error clearing cache:', error);
      throw error;
    }
  },

  /**
   * Получение детальной статистики пользователя
   */
  async getUserDetailedStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/stats/user/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения детальной статистики');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching detailed user stats:', error);
      throw error;
    }
  },

  /**
   * Получение глобальной статистики (только для админов)
   */
  async getGlobalStats() {
    try {
      const response = await fetch(`${API_BASE_URL}/ai/stats/global/`, {
        headers: getAuthHeaders(),
      });

      if (!response.ok) {
        throw new Error('Ошибка получения глобальной статистики');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching global stats:', error);
      throw error;
    }
  },

  /**
   * Получение истории AI генераций с расширенными фильтрами
   */
  async getGenerationHistoryAdvanced(filters = {}) {
    try {
      const params = new URLSearchParams();
      
      if (filters.page) params.append('page', filters.page);
      if (filters.page_size) params.append('page_size', filters.page_size);
      if (filters.status) params.append('status', filters.status);
      if (filters.style) params.append('style', filters.style);

      const response = await fetch(
        `${API_BASE_URL}/ai/history/?${params.toString()}`,
        {
          headers: getAuthHeaders(),
        }
      );

      if (!response.ok) {
        throw new Error('Ошибка получения истории');
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching advanced AI history:', error);
      throw error;
    }
  },
};

// Константы для кодов ошибок
export const AI_ERROR_CODES = {
  LIMIT_EXCEEDED: 'LIMIT_EXCEEDED',
  NOT_PREMIUM: 'NOT_PREMIUM',
  TIMEOUT: 'TIMEOUT',
  AI_ERROR: 'AI_ERROR',
  INVALID_RESPONSE: 'INVALID_RESPONSE',
  NETWORK_ERROR: 'NETWORK_ERROR',
};

// Человекочитаемые сообщения об ошибках
export const getErrorMessage = (errorCode) => {
  const messages = {
    [AI_ERROR_CODES.LIMIT_EXCEEDED]: 'Превышен дневной лимит AI генераций',
    [AI_ERROR_CODES.NOT_PREMIUM]: 'AI генерация доступна только Premium пользователям',
    [AI_ERROR_CODES.TIMEOUT]: 'Время ожидания истекло. Попробуйте позже',
    [AI_ERROR_CODES.AI_ERROR]: 'Сервера AI временно недоступны',
    [AI_ERROR_CODES.INVALID_RESPONSE]: 'AI вернул некорректный код. Попробуйте изменить промпт',
    [AI_ERROR_CODES.NETWORK_ERROR]: 'Ошибка сети. Проверьте подключение к интернету',
  };

  return messages[errorCode] || 'Неизвестная ошибка';
}; 