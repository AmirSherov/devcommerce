'use client';

import { useAuth } from '../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Loader from '../../../components/simple-loader';
import ProfileHeader from './components/ProfileHeader';
import OverviewTab from './components/OverviewTab';
import ProjectsTab from './components/ProjectsTab';
import PortfolioTab from './components/PortfolioTab';
import DevIssueTab from './components/DevIssueTab';

export default function ProfilePage() {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();
  const [mounted, setMounted] = useState(false);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    if (mounted && !isLoading && !isAuthenticated) {
      router.push('/auth');
    }
  }, [mounted, isAuthenticated, isLoading, router]);

  if (!mounted || isLoading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
        <Loader text="Загрузка профиля..." fullScreen={true} />
      </div>
    );
  }

  if (!isAuthenticated || !user) {
    return null;
  }

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewTab />;
      case 'projects':
        return <ProjectsTab />;
      case 'portfolio':
        return <PortfolioTab />;
      case 'devissue':
        return <DevIssueTab />;
      default:
        return <OverviewTab />;
    }
  };

  return (
    <div className="min-h-screen bg-black text-white">
      {/* Top Navigation */}
      <nav className="bg-black border-b border-gray-800 px-6 py-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <button 
            onClick={() => router.push('/dashboard')}
            className="group flex items-center space-x-3 text-gray-400 hover:text-white transition-all duration-300 px-4 py-2 rounded-lg hover:bg-gray-800/50"
          >
            <div className="w-8 h-8 rounded-lg bg-gray-800 flex items-center justify-center group-hover:bg-gray-700 transition-colors">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
              </svg>
            </div>
            <span className="font-medium">Назад к дашборду</span>
          </button>
          
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <h1 className="text-xl font-bold text-white">
              Профиль пользователя
            </h1>
          </div>
          
          <div className="w-32"></div>
        </div>
      </nav>

      {/* Profile Header with Tabs */}
      <ProfileHeader 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />

      {/* Tab Content */}
      <div className="bg-black min-h-screen">
        {renderTabContent()}
      </div>
    </div>
  );
} 