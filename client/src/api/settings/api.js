import { setAuthToken, getAuthToken, removeAuthToken, isAuthenticated, getAuthHeaders, getSessionHeaders } from '../../lib/auth-utils';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json();
  
  if (!response.ok) {
    const errorMessage = data.message || data.error || data.detail || 'An error occurred';
    throw new Error(`${response.status}: ${errorMessage}`);
  }
  
  return data;
};

// API функции для настроек пользователя
export const settingsAPI = {
  // ===== ПРОФИЛЬ =====
  
  // Получить настройки профиля
  getProfile: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/profile/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // Обновить настройки профиля
  updateProfile: async (profileData) => {
    const response = await fetch(`${API_BASE_URL}/settings/profile/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(profileData),
    });
    return await handleResponse(response);
  },

  // Загрузить аватар
  uploadAvatar: async (avatarFile) => {
    const formData = new FormData();
    formData.append('avatar', avatarFile);

    const response = await fetch(`${API_BASE_URL}/settings/avatar/upload/`, {
      method: 'POST',
      headers: {
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: formData,
    });
    return await handleResponse(response);
  },

  // ===== УВЕДОМЛЕНИЯ =====
  
  // Получить настройки уведомлений
  getNotificationSettings: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/notifications/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // Обновить настройки уведомлений
  updateNotificationSettings: async (settingsData) => {
    const response = await fetch(`${API_BASE_URL}/settings/notifications/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(settingsData),
    });
    return await handleResponse(response);
  },

  // ===== СЕССИИ =====
  
  // Получить список активных сессий
  getSessions: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/sessions/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // Завершить конкретную сессию
  terminateSession: async (sessionId) => {
    const response = await fetch(`${API_BASE_URL}/settings/sessions/${sessionId}/terminate/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // Завершить все сессии кроме текущей
  terminateAllSessions: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/sessions/terminate-all/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // ===== БЕЗОПАСНОСТЬ =====
  
  // Сменить пароль
  changePassword: async (passwordData) => {
    const response = await fetch(`${API_BASE_URL}/settings/change-password/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(passwordData),
    });
    return await handleResponse(response);
  },

  // ===== ОБЩИЕ НАСТРОЙКИ =====
  
  // Получить обзор всех настроек
  getSettingsOverview: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/overview/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },

  // Создать запись о новой сессии (вызывается при логине)
  createSessionRecord: async () => {
    const response = await fetch(`${API_BASE_URL}/settings/sessions/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    return await handleResponse(response);
  },
}; 