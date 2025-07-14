'use client';
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// API для контейнеров хранилища
export const storageAPI = {
  // Получить список контейнеров
  getContainers: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка загрузки контейнеров'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения контейнеров:', error);
      return {
        success: false,
        error: 'Ошибка загрузки контейнеров'
      };
    }
  },

  // Создать новый контейнер
  createContainer: async (containerData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(containerData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || errorData.message || 'Ошибка создания контейнера'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка создания контейнера:', error);
      return {
        success: false,
        error: error.message || 'Ошибка создания контейнера'
      };
    }
  },

  // Получить информацию о контейнере
  getContainer: async (containerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Контейнер не найден'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения контейнера:', error);
      return {
        success: false,
        error: 'Ошибка загрузки контейнера'
      };
    }
  },

  // Обновить контейнер
  updateContainer: async (containerId, containerData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: JSON.stringify(containerData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || errorData.message || 'Ошибка обновления контейнера'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка обновления контейнера:', error);
      return {
        success: false,
        error: error.message || 'Ошибка обновления контейнера'
      };
    }
  },

  // Удалить контейнер
  deleteContainer: async (containerId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || errorData.message || 'Ошибка удаления контейнера'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка удаления контейнера:', error);
      return {
        success: false,
        error: error.message || 'Ошибка удаления контейнера'
      };
    }
  },

  // Получить список файлов в контейнере
  getContainerFiles: async (containerId, page = 1, pageSize = 20) => {
    try {
      const response = await fetch(
        `${API_BASE_URL}/storage/containers/${containerId}/files/?page=${page}&page_size=${pageSize}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
          },
        }
      );
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка загрузки файлов'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения файлов контейнера:', error);
      return {
        success: false,
        error: 'Ошибка загрузки файлов'
      };
    }
  },

  // Загрузить файл в контейнер
  uploadFile: async (containerId, fileData) => {
    try {
      const formData = new FormData();
      formData.append('file', fileData.file);
      formData.append('filename', fileData.filename || '');
      formData.append('is_public', fileData.is_public || false);

      const response = await fetch(`${API_BASE_URL}/storage/containers/${containerId}/upload/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        // Возвращаем объект с ошибкой вместо выброса исключения
        return {
          success: false,
          error: errorData.error || errorData.message || 'Ошибка загрузки файла'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка загрузки файла:', error);
      return {
        success: false,
        error: error.message || 'Ошибка загрузки файла'
      };
    }
  },

  // Получить информацию о файле
  getFile: async (fileId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/files/${fileId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Файл не найден'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения файла:', error);
      return {
        success: false,
        error: 'Ошибка загрузки файла'
      };
    }
  },

  // Удалить файл
  deleteFile: async (fileId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/files/${fileId}/`, {
        method: 'DELETE',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        return {
          success: false,
          error: errorData.error || errorData.message || 'Ошибка удаления файла'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка удаления файла:', error);
      return {
        success: false,
        error: error.message || 'Ошибка удаления файла'
      };
    }
  },

  // Получить лимиты хранилища
  getStorageLimits: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/limits/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка загрузки лимитов'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения лимитов:', error);
      return {
        success: false,
        error: 'Ошибка загрузки лимитов'
      };
    }
  },

  // Получить статистику хранилища
  getStorageStats: async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/storage/stats/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('access_token')}`,
        },
      });
      
      if (!response.ok) {
        return {
          success: false,
          error: 'Ошибка загрузки статистики'
        };
      }
      
      return await response.json();
    } catch (error) {
      console.error('Ошибка получения статистики:', error);
      return {
        success: false,
        error: 'Ошибка загрузки статистики'
      };
    }
  },
}; 