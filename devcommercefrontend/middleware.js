import { NextResponse } from 'next/server';

const protectedRoutes = [
  '/dashboard',
  '/u/me',
  '/u/me/portfolio',
  '/u/me/portfolio/create'
];
const publicOnlyRoutes = [
  '/auth',
  '/forgot-password',
];

function isAuthenticated(request) {
  const token = request.cookies.get('access_token')?.value || 
                request.cookies.get('token')?.value;
  
  const authHeader = request.headers.get('authorization');
  const bearerToken = authHeader?.startsWith('Bearer ') ? authHeader.slice(7) : null;
  
  return !!(token || bearerToken);
}
function isProtectedRoute(pathname) {
  return protectedRoutes.some(route => pathname.startsWith(route));
}
function isPublicOnlyRoute(pathname) {
  return publicOnlyRoutes.some(route => pathname.startsWith(route));
}

export function middleware(request) {
  const { pathname } = request.nextUrl;
  const userIsAuthenticated = isAuthenticated(request);

  console.log(`Middleware: ${pathname}, Authenticated: ${userIsAuthenticated}`);
  if (userIsAuthenticated && isPublicOnlyRoute(pathname)) {
    console.log(`Redirecting authenticated user from ${pathname} to /dashboard`);
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }
  if (!userIsAuthenticated && isProtectedRoute(pathname)) {
    console.log(`Redirecting unauthenticated user from ${pathname} to /auth`);
    return NextResponse.redirect(new URL('/auth', request.url));
  }

  // Если все проверки пройдены, разрешаем доступ
  return NextResponse.next();
}
export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}; 