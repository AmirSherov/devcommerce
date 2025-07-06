# Система безопасности маршрутов

## Обзор

В проекте реализована многоуровневая система защиты маршрутов:

1. **Middleware** - защита на уровне сервера (первый уровень)
2. **ProtectedRoute компонент** - защита на уровне клиента (второй уровень)
3. **useAuth хук** - проверка в компонентах (третий уровень)

## Middleware (`middleware.js`)

### Защищенные маршруты (требуют авторизации)
```javascript
const protectedRoutes = [
  '/dashboard',
  '/profile',
  '/settings',
  '/orders',
  '/admin',
];
```

### Публичные маршруты (только для неавторизованных)
```javascript
const publicOnlyRoutes = [
  '/auth',
  '/login',
  '/register',
  '/forgot-password',
];
```

### Как работает

1. **Проверка токена**: Middleware проверяет наличие токена в cookies или Authorization header
2. **Редирект авторизованных**: Если пользователь авторизован и пытается попасть на `/auth`, его перенаправляет на `/dashboard`
3. **Редирект неавторизованных**: Если пользователь не авторизован и пытается попасть на защищенные страницы, его перенаправляет на `/auth`

### Логирование
Middleware выводит в консоль информацию о каждом запросе:
```
Middleware: /dashboard, Authenticated: true
Redirecting unauthenticated user from /dashboard to /auth
```

## Утилиты аутентификации (`lib/auth-utils.js`)

### Функции
- `setAuthToken(token)` - сохраняет токен в localStorage и cookies
- `getAuthToken()` - получает токен из localStorage
- `removeAuthToken()` - удаляет токен из localStorage и cookies
- `isAuthenticated()` - проверяет наличие токена
- `getAuthHeaders()` - возвращает заголовки для API запросов

### Cookies для Middleware
Токены сохраняются в cookies с настройками безопасности:
```javascript
document.cookie = `access_token=${token}; path=/; max-age=86400; secure; samesite=strict`;
```

## ProtectedRoute компонент

### Использование

Для защищенных страниц:
```jsx
<ProtectedRoute requireAuth={true}>
  <YourProtectedContent />
</ProtectedRoute>
```

Для публичных страниц (только для неавторизованных):
```jsx
<ProtectedRoute requireAuth={false}>
  <AuthForm />
</ProtectedRoute>
```

### Параметры
- `requireAuth` - требуется ли авторизация (по умолчанию `true`)
- `redirectTo` - куда перенаправлять неавторизованных (по умолчанию `/auth`)

## Добавление новых защищенных маршрутов

1. **В middleware**: Добавь путь в массив `protectedRoutes`
```javascript
const protectedRoutes = [
  '/dashboard',
  '/profile',
  '/your-new-route', // ← добавь сюда
];
```

2. **В компоненте**: Оберни страницу в `ProtectedRoute`
```jsx
export default function YourNewPage() {
  return (
    <ProtectedRoute requireAuth={true}>
      {/* содержимое страницы */}
    </ProtectedRoute>
  );
}
```

## Отладка

### Проверка токенов
```javascript
// В браузерной консоли
localStorage.getItem('access_token'); // проверить localStorage
document.cookie; // проверить cookies
```

### Логи middleware
Middleware выводит подробные логи в консоль сервера Next.js.

## Безопасность

### Настройки cookies
- `secure` - передача только по HTTPS
- `samesite=strict` - защита от CSRF атак
- `max-age=86400` - время жизни 24 часа

### Множественная проверка
Система проверяет токены в нескольких местах:
1. localStorage (для клиентских компонентов)
2. Cookies (для middleware)
3. Authorization header (для API запросов)

## Примеры использования

### Создание новой защищенной страницы
```jsx
// app/settings/page.tsx
import ProtectedRoute from "@/components/ProtectedRoute";

export default function SettingsPage() {
  return (
    <ProtectedRoute requireAuth={true}>
      <div>
        <h1>Настройки</h1>
        {/* содержимое */}
      </div>
    </ProtectedRoute>
  );
}
```

### Создание публичной страницы
```jsx
// app/forgot-password/page.tsx
import ProtectedRoute from "@/components/ProtectedRoute";

export default function ForgotPasswordPage() {
  return (
    <ProtectedRoute requireAuth={false}>
      <div>
        <h1>Восстановление пароля</h1>
        {/* форма восстановления */}
      </div>
    </ProtectedRoute>
  );
}
``` 