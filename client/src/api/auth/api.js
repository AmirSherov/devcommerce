import { setAuthToken, getAuthToken, removeAuthToken, isAuthenticated, getAuthHeaders, setSessionKey, getSessionKey, removeSessionKey, getSessionHeaders } from '../../lib/auth-utils';

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// Универсальный обработчик ошибок авторизации
function handleAuthError(status, errorMessage) {
  const isAuthError =
    status === 401 ||
    /session has been terminated|invalid token|unauthorized/i.test(errorMessage);
  if (isAuthError && typeof window !== 'undefined') {
    removeAuthToken();
    removeSessionKey();
    window.location.href = '/auth';
  }
}

// Helper function to handle API responses
const handleResponse = async (response) => {
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const errorMessage = data.message || data.error || data.detail || 'An error occurred';
    handleAuthError(response.status, errorMessage);
    throw new Error(`${response.status}: ${errorMessage}`);
  }
  return data;
};

// Authentication API functions
export const authAPI = {
  // Register new user
  register: async (userData) => {
    const response = await fetch(`${API_BASE_URL}/auth/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(userData),
    });
    
    const data = await handleResponse(response);
    
    // Store token if registration successful
    if (data.token) {
      setAuthToken(data.token);
    }
    // Store session_key if present
    if (data.session_key) {
      setSessionKey(data.session_key);
    }
    
    return data;
  },

  // Login user
  login: async (credentials) => {
    const response = await fetch(`${API_BASE_URL}/auth/login/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(credentials),
    });
    
    const data = await handleResponse(response);
    
    // Store token if login successful
    if (data.token) {
      setAuthToken(data.token);
    }
    // Store session_key if present
    if (data.session_key) {
      setSessionKey(data.session_key);
    }
    
    return data;
  },

  // Logout user
  logout: async () => {
    try {
      // Отправить запрос на сервер для logout
      const response = await fetch(`${API_BASE_URL}/auth/logout/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...getAuthHeaders(),
          ...getSessionHeaders(),
        },
      });

      // Очистить токены из localStorage независимо от ответа сервера
      removeAuthToken();
      removeSessionKey();

      // Если запрос успешен, возвращаем результат
      if (response.ok) {
        const data = await response.json();
        return data;
      } else {
        // Если ошибка на сервере, всё равно очищаем локальные данные
        console.warn('Server logout failed, but local data cleared');
        return { message: 'Logged out locally' };
      }
    } catch (error) {
      // Если сеть недоступна, всё равно очищаем локальные данные
      removeAuthToken();
      removeSessionKey();
      console.warn('Network error during logout, but local data cleared');
      return { message: 'Logged out locally' };
    }
  },

  // Get current user data
  me: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/me/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Update user profile
  updateProfile: async (profileData) => {
    const response = await fetch(`${API_BASE_URL}/auth/update-profile/`, {
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

  // Request password reset
  requestPasswordReset: async (email) => {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset-request/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify({ email }),
    });
    
    return await handleResponse(response);
  },

  // Confirm password reset with code
  confirmPasswordReset: async (resetData) => {
    const response = await fetch(`${API_BASE_URL}/auth/password-reset-confirm/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify(resetData),
    });
    
    return await handleResponse(response);
  },

  // Change password for authenticated user
  changePassword: async (passwordData) => {
    const response = await fetch(`${API_BASE_URL}/auth/change-password/`, {
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

  // Verify email with code
  verifyEmail: async (code) => {
    const response = await fetch(`${API_BASE_URL}/auth/verify-email/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
      body: JSON.stringify({ code }),
    });
    
    return await handleResponse(response);
  },

  // Resend email verification code
  resendVerificationCode: async () => {
    const response = await fetch(`${API_BASE_URL}/auth/resend-verification/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Check if user is authenticated
  isAuthenticated,

  // Get stored token
  getToken: getAuthToken,
}; 