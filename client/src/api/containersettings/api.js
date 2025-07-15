const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

export const containerSettingsAPI = {
  // Получить детальную статистику контейнера
  getContainerStats: async (containerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/stats/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка получения статистики контейнера'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка получения статистики контейнера' };
    }
  },

  // Получить логи API по контейнеру
  getContainerLogs: async (containerId, page = 1, pageSize = 20) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/logs/?page=${page}&page_size=${pageSize}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка получения логов API'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка получения логов API' };
    }
  },

  // Получить API ключ для публичного API
  getPublicApiKey: async (containerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/remote/storage/keys/?container_id=${containerId}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка получения API ключа'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка получения API ключа' };
    }
  },

  // Получить расширенную статистику публичного API
  getPublicApiStats: async (containerId = null) => {
    try {
      const url = containerId 
        ? `${API_BASE_URL}/remote/storage/stats/?container_id=${containerId}`
        : `${API_BASE_URL}/remote/storage/stats/`;
        
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка получения статистики публичного API'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка получения статистики публичного API' };
    }
  },

  // Создать новый API ключ для контейнера
  createPublicApiKey: async (containerId, keyData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/remote/storage/keys/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify({
          container_id: containerId,
          ...keyData
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Ошибка создания API ключа'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка создания API ключа' };
    }
  },

  // Обновить настройки API ключа
  updateApiKeySettings: async (containerId, settings) => {
    try {
      const response = await fetch(`${API_BASE_URL}/remote/storage/keys/${containerId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(settings),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || 'Ошибка обновления настроек API ключа'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка обновления настроек API ключа' };
    }
  },

  // Получить лимиты для плана пользователя
  getApiLimits: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/remote/storage/limits/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка получения лимитов API'
        };
      }
      
      return await response.json();
    } catch (error) {
      return { success: false, error: error.message || 'Ошибка получения лимитов API' };
    }
  },
}; 