'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '../../contexts/AuthContext';
import { Sidebar, SidebarBody, SidebarLink, useSidebar } from './sidebar';
import { motion } from 'motion/react';
import { cn } from '../../lib/utils';

// Иконки для sidebar
const DashboardIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7"></rect>
    <rect x="14" y="3" width="7" height="7"></rect>
    <rect x="14" y="14" width="7" height="7"></rect>
    <rect x="3" y="14" width="7" height="7"></rect>
  </svg>
);

const ProfileIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
    <circle cx="12" cy="7" r="4"></circle>
  </svg>
);

const TemplatesIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
    <circle cx="8.5" cy="8.5" r="1.5"></circle>
    <polyline points="21,15 16,10 5,21"></polyline>
  </svg>
);

const PortfolioIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
  </svg>
);

const SettingsIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="3"></circle>
    <path d="M12 1v6m0 6v6m11-7h-6m-6 0H1m18-4a9 9 0 1 1-18 0 9 9 0 0 1 18 0z"></path>
  </svg>
);

const LogoutIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
    <polyline points="16,17 21,12 16,7"></polyline>
    <line x1="21" y1="12" x2="9" y2="12"></line>
  </svg>
);

const ProjectsIcon = () => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M19 21V5a2 2 0 0 0-2-2H7a2 2 0 0 0-2 2v16m14 0H5"></path>
    <line x1="12" y1="12" x2="12" y2="12"></line>
    <line x1="12" y1="8" x2="12" y2="12"></line>
    <line x1="12" y1="16" x2="12" y2="16"></line>
  </svg>
);
  
interface DashboardLayoutProps {
  children: React.ReactNode;
  activePage?: string;
}

export default function DashboardLayout({ children, activePage = 'dashboard' }: DashboardLayoutProps) {
  const { user, logout } = useAuth();
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await logout();
      router.push('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  const links = [
    {
      label: "Dashboard",
      href: "/dashboard",
      icon: <DashboardIcon />,
      id: "dashboard"
    },
    {
      label: "Профиль",
      href: "/u/me",
      icon: <ProfileIcon />,
      id: "profile"
    },
    {
      label: "Портфолио",
      href: "/portfolio/edit/me",
      icon: <PortfolioIcon />,
      id: "portfolio"
    },
    {
      label: "Шаблоны",
      href: "/templates/portfolio",
      icon: <TemplatesIcon />,
      id: "templates"
    },
    {
      label: "Проекты",
      href: "/projects",
      icon: <ProjectsIcon />,
      id: "projects"
    },
    {
      label: "Настройки",
      href: "/settings",
      icon: <SettingsIcon />,
      id: "settings"
    },
    {
      label: "Выход",
      href: "#",
      icon: <LogoutIcon />,
      id: "logout"
    },
  ];

  const SidebarLogo = () => {
    const { open, animate } = useSidebar();
    return (
      <div
        className="flex items-center py-3 px-3 cursor-pointer min-h-[48px]"
        onClick={() => router.push('/')}
      >
        <div className="h-6 w-6 bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg flex items-center justify-center flex-shrink-0">
          <span className="text-white font-bold text-xs">D</span>
        </div>
        <motion.span
          className="font-medium text-white whitespace-nowrap ml-3"
          animate={{
            display: animate ? (open ? 'inline-block' : 'none') : 'inline-block',
            opacity: animate ? (open ? 1 : 0) : 1,
          }}
          initial={false}
        >
          DevCommerce
        </motion.span>
      </div>
    );
  };

  return (
    <div className={cn(
      "flex flex-col md:flex-row bg-black w-full mx-auto",
      "min-h-screen md:h-screen"
    )}>
      <Sidebar>
        <SidebarBody className="justify-between gap-10 bg-black border-r border-gray-800">
          <div className="flex flex-col flex-1 overflow-y-auto overflow-x-hidden">
            {/* Logo */}
            <SidebarLogo />

            <div className="mt-8 flex flex-col gap-1">
              {links.map((link, idx) => (
                <div 
                  key={idx} 
                  onClick={() => {
                    if (link.id === 'logout') {
                      handleLogout();
                    } else {
                      router.push(link.href);
                    }
                  }}
                >
                  <SidebarLink 
                    link={link}
                    className={cn(
                      "cursor-pointer hover:bg-gray-800 rounded-lg transition-colors text-gray-300 hover:text-white w-full flex items-center",
                      activePage === link.id ? "bg-gray-800 text-white" : ""
                    )}
                  />
                </div>
              ))}
            </div>
          </div>

          {/* User Profile */}
          <div onClick={() => router.push('/u/me')} className="cursor-pointer">
            <SidebarLink
              link={{
                label: user?.username || user?.email || 'User',
                href: "#",
                icon: (
                  <div className="h-6 w-6 flex-shrink-0 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold">
                    {(user?.username || user?.email || 'U').charAt(0).toUpperCase()}
                  </div>
                ),
              }}
              className="text-gray-300 hover:text-white hover:bg-gray-800 rounded-lg transition-colors w-full flex items-center"
            />
          </div>
        </SidebarBody>
      </Sidebar>
      
      <div className="flex flex-1 md:h-screen">
        <div className="bg-black text-white flex flex-col flex-1 w-full md:h-full md:overflow-y-auto pt-16 md:pt-0">
          {children}
        </div>
      </div>
    </div>
  );
} 