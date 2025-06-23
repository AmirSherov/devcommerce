import { NextResponse } from 'next/server';

// Защищенные маршруты - пути, которые требуют авторизации
const protectedRoutes = [
  '/dashboard',
  // Добавь сюда другие защищенные маршруты
];

// Публичные маршруты - пути, доступные только неавторизованным пользователям
const publicOnlyRoutes = [
  '/auth',
  '/forgot-password',
];

// Функция для проверки авторизации пользователя
function isAuthenticated(request) {
  // Проверяем наличие токена в cookies или localStorage через headers
  const token = request.cookies.get('access_token')?.value || 
                request.cookies.get('token')?.value;
  
  // Также проверяем Authorization header
  const authHeader = request.headers.get('authorization');
  const bearerToken = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;
  
  return !!(token || bearerToken);
}

// Функция для проверки, является ли путь защищенным
function isProtectedRoute(pathname) {
  return protectedRoutes.some(route => pathname.startsWith(route));
}

// Функция для проверки, является ли путь публичным (только для неавторизованных)
function isPublicOnlyRoute(pathname) {
  return publicOnlyRoutes.some(route => pathname.startsWith(route));
}

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const userIsAuthenticated = isAuthenticated(request);

  console.log(`Middleware: ${pathname}, Authenticated: ${userIsAuthenticated}`);

  // Если пользователь авторизован и пытается попасть на страницы только для неавторизованных
  if (userIsAuthenticated && isPublicOnlyRoute(pathname)) {
    console.log(`Redirecting authenticated user from ${pathname} to /dashboard`);
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // Если пользователь не авторизован и пытается попасть на защищенные страницы
  if (!userIsAuthenticated && isProtectedRoute(pathname)) {
    console.log(`Redirecting unauthenticated user from ${pathname} to /auth`);
    return NextResponse.redirect(new URL('/auth', request.url));
  }

  // Если все проверки пройдены, разрешаем доступ
  return NextResponse.next();
}

// Конфигурация middleware - указываем на каких путях он должен работать
export const config = {
  matcher: [
    /*
     * Исключаем:
     * - API routes (/api/*)
     * - Static files (_next/static/*)
     * - Images и другие assets (/favicon.ico, /images/*, etc.)
     * - Root path (/)
     */
    '/((?!api|_next/static|_next/image|favicon.ico|.*\\.).*)',
  ],
}; 