// Утилиты для работы с токенами аутентификации

// Функция для установки токена в localStorage и cookies
export const setAuthToken = (token) => {
  if (typeof window !== 'undefined') {
    // Сохраняем в localStorage
    localStorage.setItem('access_token', token);
    
    // Сохраняем в cookies для middleware
    document.cookie = `access_token=${token}; path=/; max-age=86400; secure; samesite=strict`;
  }
};

// Функция для получения токена
export const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

// Функция для удаления токена
export const removeAuthToken = () => {
  if (typeof window !== 'undefined') {
    // Удаляем из localStorage
    localStorage.removeItem('access_token');
    localStorage.removeItem('token'); // Для совместимости
    
    // Удаляем из cookies
    document.cookie = 'access_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT';
  }
};

// Функция для проверки аутентификации
export const isAuthenticated = () => {
  return !!getAuthToken();
};

// Функция для получения заголовков аутентификации
export const getAuthHeaders = () => {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}; 