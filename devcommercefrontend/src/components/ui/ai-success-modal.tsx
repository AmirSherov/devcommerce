'use client';

import { useRouter } from 'next/navigation';

interface AISuccessModalProps {
  isOpen: boolean;
  onClose: () => void;
  portfolio: {
    id: string;
    title: string;
    description: string;
    public_url?: string;
    author_username: string;
  } | null;
  generationTime?: number; // время генерации в секундах
}

export default function AISuccessModal({ 
  isOpen, 
  onClose, 
  portfolio, 
  generationTime 
}: AISuccessModalProps) {
  const router = useRouter();

  if (!isOpen || !portfolio) return null;

  const handleGoToSite = () => {
    if (portfolio.public_url) {
      window.open(portfolio.public_url, '_blank');
    }
  };

  const handleEditProject = () => {
    router.push(`/portfolio/edit/me?project=${portfolio.id}`);
    onClose();
  };

  const handleViewProfile = () => {
    router.push('/u/me');
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div className="bg-black border-2 border-white rounded-lg w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-4 border-b border-white">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center">
              <span className="text-black text-lg font-bold">✓</span>
            </div>
            <h2 className="text-lg font-bold text-white">Сайт создан!</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-4">
          <div className="text-center">
            {/* Project info */}
            <div className="bg-gray-900 border border-white rounded-lg p-3 mb-4 text-left">
              <h4 className="text-white font-bold text-base mb-1">{portfolio.title}</h4>
              {portfolio.description && (
                <p className="text-gray-400 text-xs">{portfolio.description}</p>
              )}
              <div className="flex items-center justify-between text-xs mt-2">
                <span className="text-gray-400">
                  Автор: <span className="text-white">{portfolio.author_username}</span>
                </span>
                {generationTime && (
                  <span className="text-gray-400">
                    Время: <span className="text-white">{generationTime.toFixed(1)}s</span>
                  </span>
                )}
              </div>
            </div>

            {/* Features created */}
            <div className="bg-gray-900 border border-white rounded-lg p-3 mb-4">
              <h5 className="text-white font-medium mb-2 text-sm">Создано:</h5>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div className="flex items-center space-x-1">
                  <span className="text-white">•</span>
                  <span className="text-gray-300">HTML код</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-white">•</span>
                  <span className="text-gray-300">CSS стили</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-white">•</span>
                  <span className="text-gray-300">JavaScript</span>
                </div>
                <div className="flex items-center space-x-1">
                  <span className="text-white">•</span>
                  <span className="text-gray-300">Адаптивность</span>
                </div>
              </div>
            </div>

            <p className="text-gray-400 text-sm mb-4">
              Сайт готов к просмотру и редактированию
            </p>
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 border-t border-white space-y-2">
          {/* Primary action */}
          <button
            onClick={handleGoToSite}
            className="w-full px-4 py-2 bg-white hover:bg-gray-200 text-black rounded-lg transition-colors font-medium"
          >
            Открыть сайт
          </button>
          
          {/* Secondary actions */}
          <div className="flex space-x-2">
            <button
              onClick={handleEditProject}
              className="flex-1 px-3 py-2 bg-gray-800 border border-white hover:bg-gray-700 text-white rounded-lg transition-colors text-sm"
            >
              Редактировать
            </button>
            <button
              onClick={handleViewProfile}
              className="flex-1 px-3 py-2 bg-gray-800 border border-white hover:bg-gray-700 text-white rounded-lg transition-colors text-sm"
            >
              Мои проекты
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 