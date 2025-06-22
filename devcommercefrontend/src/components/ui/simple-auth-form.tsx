"use client";
import React, { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { IconBrandGithub, IconBrandGoogle } from "@tabler/icons-react";
import { AnimatedInput } from "./animated-input";
import { AnimatedButton } from "./animated-button";
import { useAuth } from "../../contexts/AuthContext";
import "../../styles/auth.scss";

export default function SimpleAuthForm() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showPasswordReset, setShowPasswordReset] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    password_confirm: '',
    first_name: '',
    last_name: '',
    username: '',
  });
  const [resetEmail, setResetEmail] = useState('');
  const [resetCode, setResetCode] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newPasswordConfirm, setNewPasswordConfirm] = useState('');
  const [resetStep, setResetStep] = useState(1); // 1: email, 2: code+password
  const [message, setMessage] = useState('');

  const { login, register, requestPasswordReset, confirmPasswordReset, isAuthenticated, error, clearError } = useAuth();
  const router = useRouter();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, router]);

  // Clear error when switching forms
  useEffect(() => {
    clearError();
    setMessage('');
  }, [isSignUp, showPasswordReset, clearError]);

  const handleInputChange = useCallback((field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
  }, []);

  const handleSubmit = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage('');

    try {
      if (isSignUp) {
        // Registration
        if (formData.password !== formData.password_confirm) {
          setMessage('Passwords do not match');
          return;
        }

        // Generate username from email if not provided
        const username = formData.username || formData.email.split('@')[0];

        await register({
          email: formData.email,
          password: formData.password,
          password_confirm: formData.password_confirm,
          first_name: formData.first_name,
          last_name: formData.last_name,
          username: username,
        });

        setMessage('Registration successful! Redirecting to dashboard...');
        setTimeout(() => router.push('/dashboard'), 1500);
      } else {
        // Login
        await login({
          email: formData.email,
          password: formData.password,
        });

        setMessage('Login successful! Redirecting to dashboard...');
        setTimeout(() => router.push('/dashboard'), 1500);
      }
    } catch (error) {
      console.error('Auth error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [isSignUp, formData, register, login, router]);

  const handlePasswordReset = useCallback(async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      if (resetStep === 1) {
        // Request reset code
        await requestPasswordReset(resetEmail);
        setMessage('Reset code sent to your email!');
        setResetStep(2);
      } else {
        // Confirm reset with code
        if (newPassword !== newPasswordConfirm) {
          setMessage('Passwords do not match');
          return;
        }

        await confirmPasswordReset({
          email: resetEmail,
          code: resetCode,
          new_password: newPassword,
          new_password_confirm: newPasswordConfirm,
        });

        setMessage('Password reset successful! You can now login.');
        setShowPasswordReset(false);
        setResetStep(1);
        setResetEmail('');
        setResetCode('');
        setNewPassword('');
        setNewPasswordConfirm('');
      }
    } catch (error) {
      console.error('Password reset error:', error);
    } finally {
      setIsLoading(false);
    }
  }, [resetStep, resetEmail, newPassword, newPasswordConfirm, resetCode, requestPasswordReset, confirmPasswordReset]);

  const resetForm = useCallback(() => {
    setShowPasswordReset(false);
    setResetStep(1);
    setMessage('');
  }, []);

  if (showPasswordReset) {
    return (
      <div className="flex items-center justify-center min-h-screen p-4">
        <div className="auth-form">
          <h2 className="form-title">
            {resetStep === 1 ? "Сброс пароля" : "Новый пароль"}
          </h2>
          <p className="form-subtitle">
            {resetStep === 1 
              ? "Введите ваш email для получения кода сброса"
              : "Введите код из email и новый пароль"
            }
          </p>

          {(message || error) && (
            <div className={`message ${error ? 'error' : 'success'}`}>
              {error || message}
            </div>
          )}

          <form onSubmit={handlePasswordReset} className="form-container">
            {resetStep === 1 ? (
              <AnimatedInput
                type="email"
                label="Email адрес"
                placeholder="ivan@example.com"
                value={resetEmail}
                onChange={(e) => setResetEmail(e.target.value)}
                required
              />
            ) : (
              <>
                <AnimatedInput
                  type="text"
                  label="Код подтверждения"
                  placeholder="123456"
                  value={resetCode}
                  onChange={(e) => setResetCode(e.target.value)}
                  maxLength={6}
                  required
                />
                <AnimatedInput
                  type="password"
                  label="Новый пароль"
                  placeholder="••••••••"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
                <AnimatedInput
                  type="password"
                  label="Подтвердите новый пароль"
                  placeholder="••••••••"
                  value={newPasswordConfirm}
                  onChange={(e) => setNewPasswordConfirm(e.target.value)}
                  required
                />
              </>
            )}

            <div className="form-controls">
              <AnimatedButton 
                type="submit" 
                variant="primary" 
                className="w-full mt-4"
                disabled={isLoading}
              >
                {isLoading ? 'Загрузка...' : (resetStep === 1 ? 'Отправить код' : 'Сбросить пароль')} →
              </AnimatedButton>

              <div className="switch-container">
                <button
                  type="button"
                  onClick={resetForm}
                  className="switch-button"
                >
                  ← Назад к входу
                </button>
              </div>
            </div>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen p-4">
      <div className="auth-form">
        <h2 className="form-title">
          {isSignUp ? "Создать аккаунт" : "Добро пожаловать"}
        </h2>
        <p className="form-subtitle">
          {isSignUp 
            ? "Присоединяйтесь к лучшей платформе для разработчиков" 
            : "Войдите в свой аккаунт DevCommerce"
          }
        </p>

        {(message || error) && (
          <div className={`message ${error ? 'error' : 'success'}`}>
            {error || message}
          </div>
        )}

        <form onSubmit={handleSubmit} className="form-container">
          {isSignUp && (
            <>
              <div className="name-row">
                <AnimatedInput
                  type="text"
                  label="Имя"
                  placeholder="Иван"
                  value={formData.first_name}
                  onChange={(e) => handleInputChange('first_name', e.target.value)}
                />
                <AnimatedInput
                  type="text"
                  label="Фамилия"
                  placeholder="Иванов"
                  value={formData.last_name}
                  onChange={(e) => handleInputChange('last_name', e.target.value)}
                />
              </div>
              <AnimatedInput
                type="text"
                label="Имя пользователя"
                placeholder="ivan_ivanov"
                value={formData.username}
                onChange={(e) => handleInputChange('username', e.target.value)}
              />
            </>
          )}
          
          <AnimatedInput
            type="email"
            label="Email адрес"
            placeholder="ivan@example.com"
            value={formData.email}
            onChange={(e) => handleInputChange('email', e.target.value)}
            required
          />
          
          <AnimatedInput
            type="password"
            label="Пароль"
            placeholder="••••••••"
            value={formData.password}
            onChange={(e) => handleInputChange('password', e.target.value)}
            required
          />
          
          {isSignUp && (
            <AnimatedInput
              type="password"
              label="Подтвердите пароль"
              placeholder="••••••••"
              value={formData.password_confirm}
              onChange={(e) => handleInputChange('password_confirm', e.target.value)}
              required
            />
          )}

          <div className="form-controls">
            {!isSignUp && (
              <div className="remember-row">
                <label className="checkbox-label">
                  <input type="checkbox" />
                  Запомнить меня
                </label>
                <button
                  type="button"
                  onClick={() => setShowPasswordReset(true)}
                  className="forgot-link"
                >
                  Забыли пароль?
                </button>
              </div>
            )}

            <AnimatedButton 
              type="submit" 
              variant="primary" 
              className="w-full mt-4"
              disabled={isLoading}
            >
              {isLoading ? 'Загрузка...' : (isSignUp ? "Создать аккаунт" : "Войти")} →
            </AnimatedButton>

            <div className="switch-container">
              <span className="switch-text">
                {isSignUp ? "Уже есть аккаунт? " : "Нет аккаунта? "}
              </span>
              <button
                type="button"
                onClick={() => setIsSignUp(!isSignUp)}
                className="switch-button"
              >
                {isSignUp ? "Войти" : "Зарегистрироваться"}
              </button>
            </div>

            <div className="divider"></div>

            <div className="social-buttons">
              <AnimatedButton type="button" variant="social" className="w-full">
                <IconBrandGithub size={20} />
                <span>Продолжить с GitHub</span>
              </AnimatedButton>
              <AnimatedButton type="button" variant="social" className="w-full">
                <IconBrandGoogle size={20} />
                <span>Продолжить с Google</span>
              </AnimatedButton>
            </div>
          </div>
        </form>
      </div>
    </div>
  );
}

 