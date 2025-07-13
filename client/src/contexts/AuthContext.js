'use client';

import React, { createContext, useContext, useReducer, useEffect, useCallback } from 'react';
import { authAPI } from '../api/auth/api';
import { removeSessionKey } from '../lib/auth-utils';

// Initial state
const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
};

// Action types
const AUTH_ACTIONS = {
  SET_LOADING: 'SET_LOADING',
  SET_USER: 'SET_USER',
  SET_ERROR: 'SET_ERROR',
  LOGOUT: 'LOGOUT',
  CLEAR_ERROR: 'CLEAR_ERROR',
};

// Reducer
const authReducer = (state, action) => {
  switch (action.type) {
    case AUTH_ACTIONS.SET_LOADING:
      return {
        ...state,
        isLoading: action.payload,
      };
    
    case AUTH_ACTIONS.SET_USER:
      return {
        ...state,
        user: action.payload,
        isAuthenticated: !!action.payload,
        isLoading: false,
        error: null,
      };
    
    case AUTH_ACTIONS.SET_ERROR:
      return {
        ...state,
        error: action.payload,
        isLoading: false,
      };
    
    case AUTH_ACTIONS.LOGOUT:
      return {
        ...state,
        user: null,
        isAuthenticated: false,
        isLoading: false,
        error: null,
      };
    
    case AUTH_ACTIONS.CLEAR_ERROR:
      return {
        ...state,
        error: null,
      };
    
    default:
      return state;
  }
};

// Create context
const AuthContext = createContext();

// Auth provider component
export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  const checkAuthStatus = useCallback(async () => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      
      if (!authAPI.isAuthenticated()) {
        dispatch({ type: AUTH_ACTIONS.SET_USER, payload: null });
        return;
      }

      const response = await authAPI.me();
      dispatch({ type: AUTH_ACTIONS.SET_USER, payload: response.user });
    } catch (error) {
      console.error('Auth check failed:', error);
      
      // Только если ошибка 401 (Unauthorized), делаем logout
      if (error.message.includes('401') || error.message.includes('Unauthorized') || error.message.includes('Invalid token')) {
        authAPI.logout();
        dispatch({ type: AUTH_ACTIONS.SET_USER, payload: null });
      } else {
        // Для других ошибок не делаем logout, просто логируем
        console.warn('Auth check failed but not logging out:', error.message);
      }
    }
  }, []);

  // Check authentication status on mount only
  useEffect(() => {
    checkAuthStatus();
  }, [checkAuthStatus]);

  const login = useCallback(async (credentials) => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      
      const response = await authAPI.login(credentials);
      dispatch({ type: AUTH_ACTIONS.SET_USER, payload: response.user });
      
      return response;
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const register = useCallback(async (userData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.SET_LOADING, payload: true });
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      
      const response = await authAPI.register(userData);
      dispatch({ type: AUTH_ACTIONS.SET_USER, payload: response.user });
      
      return response;
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const logout = useCallback(async () => {
    try {
      await authAPI.logout();
      removeSessionKey();
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    } catch (error) {
      console.error('Logout error:', error);
      // Force logout even if API call fails
      dispatch({ type: AUTH_ACTIONS.LOGOUT });
    }
  }, []);

  const updateProfile = useCallback(async (profileData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      
      const response = await authAPI.updateProfile(profileData);
      dispatch({ type: AUTH_ACTIONS.SET_USER, payload: response.user });
      
      return response;
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const requestPasswordReset = useCallback(async (email) => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      return await authAPI.requestPasswordReset(email);
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const confirmPasswordReset = useCallback(async (resetData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      return await authAPI.confirmPasswordReset(resetData);
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const changePassword = useCallback(async (passwordData) => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      return await authAPI.changePassword(passwordData);
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const verifyEmail = useCallback(async (code) => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      const response = await authAPI.verifyEmail(code);
      
      // Refresh user data after email verification
      await checkAuthStatus();
      
      return response;
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, [checkAuthStatus]);

  const resendVerificationCode = useCallback(async () => {
    try {
      dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
      return await authAPI.resendVerificationCode();
    } catch (error) {
      dispatch({ type: AUTH_ACTIONS.SET_ERROR, payload: error.message });
      throw error;
    }
  }, []);

  const clearError = useCallback(() => {
    dispatch({ type: AUTH_ACTIONS.CLEAR_ERROR });
  }, []);

  const value = {
    ...state,
    login,
    register,
    logout,
    updateProfile,
    requestPasswordReset,
    confirmPasswordReset,
    changePassword,
    verifyEmail,
    resendVerificationCode,
    clearError,
    checkAuthStatus,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext; 