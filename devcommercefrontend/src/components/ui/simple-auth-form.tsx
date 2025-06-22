"use client";
import React, { useState } from "react";
import { IconBrandGithub, IconBrandGoogle } from "@tabler/icons-react";
import { AnimatedInput } from "./animated-input";
import { AnimatedButton } from "./animated-button";
import "../../styles/auth.scss";

export default function SimpleAuthForm() {
  const [isSignUp, setIsSignUp] = useState(false);

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    console.log(isSignUp ? "Sign up submitted" : "Sign in submitted");
  };

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

        <form onSubmit={handleSubmit} className="form-container">
          {isSignUp && (
            <div className="name-row">
              <AnimatedInput
                type="text"
                label="Имя"
                placeholder="Иван"
                required
              />
              <AnimatedInput
                type="text"
                label="Фамилия"
                placeholder="Иванов"
                required
              />
            </div>
          )}
          
          <AnimatedInput
            type="email"
            label="Email адрес"
            placeholder="ivan@example.com"
            required
          />
          
          <AnimatedInput
            type="password"
            label="Пароль"
            placeholder="••••••••"
            required
          />
          
          {isSignUp && (
            <AnimatedInput
              type="password"
              label="Подтвердите пароль"
              placeholder="••••••••"
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
                <a href="#" className="forgot-link">
                  Забыли пароль?
                </a>
              </div>
            )}

            <AnimatedButton type="submit" variant="primary" className="w-full mt-4">
              {isSignUp ? "Создать аккаунт" : "Войти"} →
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

 