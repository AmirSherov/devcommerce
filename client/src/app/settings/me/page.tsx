'use client';
import React, { useState } from 'react';
import ProfileSettings from './components/ProfileSettings';
import PrivacySettings from './components/PrivacySettings';
import NotificationSettings from './components/NotificationSettings';
import SecuritySettings from './components/SecuritySettings';
import styles from './settings.module.scss';
import DashboardLayout from '@/components/ui/dashboard-layout';
const TABS = [
  { id: 'profile', label: 'Профиль' },
  { id: 'privacy', label: 'Приватность' },
  { id: 'notifications', label: 'Уведомления' },
  { id: 'security', label: 'Безопасность' },
];

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState('profile');

  return (
   <DashboardLayout activePage="settings">
     <div className={styles.settingsLayout}>
      <aside className={styles.sidebar}>
        <h1 className={styles.title}>Настройки</h1>
        <nav className={styles.tabsVertical}>
          {TABS.map(tab => (
            <button
              key={tab.id}
              className={activeTab === tab.id ? styles.activeTabV : styles.tabV}
              onClick={() => setActiveTab(tab.id)}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </aside>
      <main className={styles.mainContent}>
        {activeTab === 'profile' && <ProfileSettings />}
        {activeTab === 'privacy' && <PrivacySettings />}
        {activeTab === 'notifications' && <NotificationSettings />}
        {activeTab === 'security' && <SecuritySettings />}
      </main>
    </div>
   </DashboardLayout>
  );
} 