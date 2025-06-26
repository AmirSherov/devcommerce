'use client';
import { HiLockClosed } from "react-icons/hi2";
interface PremiumRequiredModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUpgrade?: () => void;
}

export default function PremiumRequiredModal({ isOpen, onClose, onUpgrade }: PremiumRequiredModalProps) {
  if (!isOpen) return null;

  const handleUpgrade = () => {
    if (onUpgrade) {
      onUpgrade();
    } else {
      window.location.href = '/dashboard';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-90 flex items-center justify-center z-50 p-4">
      <div className="bg-black border-2 border-white rounded-lg w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-white">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-white rounded-lg flex items-center justify-center">
              <span className="text-black text-xl"><HiLockClosed /></span>
            </div>
            <h2 className="text-xl font-bold text-white">Premium Required</h2>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="text-center">
            {/* Icon */}
            <div className="w-20 h-20 mx-auto mb-6 bg-white rounded-full flex items-center justify-center">
              <span className="text-black text-4xl font-bold">AI</span>
            </div>

            {/* Title */}
            <h3 className="text-2xl font-bold text-white mb-4">
              AI Генератор доступен только<br/>Premium пользователям
            </h3>

            {/* Description */}
            <p className="text-gray-400 mb-6 leading-relaxed">
              Получите доступ к мощному AI генератору сайтов и создавайте профессиональные проекты за секунды
            </p>

            {/* Features */}
            <div className="space-y-3 mb-8 text-left">
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-white">До 5 AI генераций в день</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-white">6 профессиональных стилей</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-white">Быстрая генерация кода</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-white">Адаптивный дизайн</span>
              </div>
              
              <div className="flex items-center space-x-3">
                <div className="w-6 h-6 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-4 h-4 text-black" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
                <span className="text-white">Шаблоны промптов</span>
              </div>
            </div>

            {/* Price hint */}
            <div className="bg-gray-900 border border-white rounded-lg p-4 mb-6">
              <div className="flex items-center justify-center space-x-2">
                <span className="text-gray-400 line-through">$19.99</span>
                <span className="text-2xl font-bold text-white">$9.99</span>
                <span className="text-white">/месяц</span>
              </div>
              <p className="text-gray-400 text-sm mt-1">Скидка 50% в первый месяц!</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-white space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-gray-800 border border-white hover:bg-gray-700 text-white rounded-lg transition-colors font-medium"
          >
            Позже
          </button>
          <button
            onClick={handleUpgrade}
            className="flex-1 px-4 py-3 bg-white hover:bg-gray-200 text-black rounded-lg transition-all font-medium"
          >
            Обновить до Premium
          </button>
        </div>
      </div>
    </div>
  );
} 