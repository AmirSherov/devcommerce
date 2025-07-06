'use client';

import { useAuth } from '../../../contexts/AuthContext';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import Loader from '../../../components/simple-loader';
import DashboardLayout from '../../../components/ui/dashboard-layout';
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
    <DashboardLayout activePage="profile">
      {/* Profile Header with Tabs */}
      <ProfileHeader 
        activeTab={activeTab} 
        onTabChange={setActiveTab} 
      />

      {/* Tab Content */}
      <div className="mt-6">
        {renderTabContent()}
      </div>
    </DashboardLayout>
  );
} 