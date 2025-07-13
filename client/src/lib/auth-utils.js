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

// ===== Работа с session_key =====
export const setSessionKey = (sessionKey) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('session_key', sessionKey);
  }
};

export const getSessionKey = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('session_key');
  }
  return null;
};

export const removeSessionKey = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('session_key');
  }
};

export const getSessionHeaders = () => {
  const sessionKey = getSessionKey();
  return sessionKey ? { 'X-Session-Key': sessionKey } : {};
}; 

export { setSessionKey, getSessionKey, removeSessionKey, getSessionHeaders }; 