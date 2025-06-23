'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '../contexts/AuthContext';
import SimpleLoader from './simple-loader';

const ProtectedRoute = ({ children, requireAuth = true, redirectTo = '/auth' }) => {
  const { isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading) {
      if (requireAuth && !isAuthenticated) {
        router.push(redirectTo);
      } else if (!requireAuth && isAuthenticated) {
        router.push('/dashboard');
      }
    }
  }, [isAuthenticated, isLoading, requireAuth, redirectTo, router]);
  if (isLoading) {
    return <SimpleLoader />;
  }
  if (requireAuth && !isAuthenticated) {
    return null;
  }
  if (!requireAuth && isAuthenticated) {
    return null;
  }
  return children;
};

export default ProtectedRoute; 