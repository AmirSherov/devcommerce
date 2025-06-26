'use client';

interface AIUnavailableModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRetry?: () => void;
  errorMessage?: string;
}

export default function AIUnavailableModal({ 
  isOpen, 
  onClose, 
  onRetry, 
  errorMessage 
}: AIUnavailableModalProps) {
  if (!isOpen) return null;

  const handleRetry = () => {
    if (onRetry) {
      onRetry();
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 border-2 border-white rounded-lg w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-red-500 to-orange-600 rounded-lg flex items-center justify-center">
              <span className="text-white text-xl">⚠️</span>
            </div>
            <h2 className="text-xl font-bold text-white">AI Недоступен</h2>
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
            <div className="w-20 h-20 mx-auto mb-6 bg-gradient-to-r from-red-500 to-orange-600 rounded-full flex items-center justify-center">
              <span className="text-white text-4xl">🤖</span>
            </div>

            {/* Title */}
            <h3 className="text-2xl font-bold text-white mb-4">
              AI сервера временно недоступны
            </h3>

            {/* Description */}
            <div className="space-y-3 mb-6">
              <p className="text-gray-400 leading-relaxed">
                {errorMessage || 'В данный момент сервера AI испытывают высокую нагрузку. Попробуйте через несколько минут.'}
              </p>
              
              <div className="bg-gray-800 border border-gray-600 rounded-lg p-4">
                <div className="flex items-center space-x-2 mb-2">
                  <span className="text-yellow-400">🔄</span>
                  <span className="text-white font-medium">Что можно сделать:</span>
                </div>
                <ul className="text-gray-400 text-sm space-y-1 text-left">
                  <li>• Попробовать через 2-3 минуты</li>
                  <li>• Проверить интернет соединение</li>
                  <li>• Изменить промпт на более простой</li>
                  <li>• Создать портфолио вручную</li>
                </ul>
              </div>
            </div>

            {/* Status indicator */}
            <div className="bg-gray-800 border border-gray-600 rounded-lg p-4 mb-6">
              <div className="flex items-center justify-between">
                <span className="text-white font-medium">Статус серверов:</span>
                <div className="flex items-center space-x-2">
                  <div className="w-3 h-3 bg-red-500 rounded-full animate-pulse"></div>
                  <span className="text-red-400">Недоступны</span>
                </div>
              </div>
              <p className="text-gray-400 text-sm mt-2">
                Мы работаем над решением проблемы
              </p>
            </div>

            {/* Alternative options */}
            <div className="bg-blue-900 bg-opacity-30 border border-blue-600 rounded-lg p-4">
              <div className="flex items-center space-x-2 mb-2">
                <span className="text-blue-400">💡</span>
                <span className="text-blue-400 font-medium">Совет:</span>
              </div>
              <p className="text-blue-300 text-sm">
                Пока AI недоступен, вы можете создать портфолио вручную в нашем редакторе с готовыми шаблонами
              </p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between p-6 border-t border-gray-700 space-x-3">
          <button
            onClick={onClose}
            className="flex-1 px-4 py-3 bg-gray-700 hover:bg-gray-600 text-white rounded-lg transition-colors font-medium"
          >
            Закрыть
          </button>
          {onRetry && (
            <button
              onClick={handleRetry}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-500 to-purple-600 hover:from-blue-600 hover:to-purple-700 text-white rounded-lg transition-all font-medium"
            >
              🔄 Попробовать снова
            </button>
          )}
        </div>
      </div>
    </div>
  );
} 