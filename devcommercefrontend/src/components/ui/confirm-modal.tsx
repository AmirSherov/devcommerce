'use client';

import Modal from './modal';

interface ConfirmModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  title: string;
  message: string;
  confirmText?: string;
  cancelText?: string;
  type?: 'danger' | 'warning' | 'info';
  isLoading?: boolean;
}

export default function ConfirmModal({
  isOpen,
  onClose,
  onConfirm,
  title,
  message,
  confirmText = 'Подтвердить',
  cancelText = 'Отмена',
  type = 'danger',
  isLoading = false,
}: ConfirmModalProps) {
  
  const handleConfirm = () => {
    onConfirm();
  };

  // Иконки для разных типов
  const getIcon = () => {
    switch (type) {
      case 'danger':
        return (
          <div className="w-12 h-12 mx-auto mb-4 bg-red-900/20 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-red-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        );
      case 'warning':
        return (
          <div className="w-12 h-12 mx-auto mb-4 bg-yellow-900/20 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-yellow-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        );
      case 'info':
        return (
          <div className="w-12 h-12 mx-auto mb-4 bg-blue-900/20 rounded-full flex items-center justify-center">
            <svg className="w-6 h-6 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        );
      default:
        return null;
    }
  };

  // Стили кнопки подтверждения в зависимости от типа
  const getConfirmButtonStyles = () => {
    switch (type) {
      case 'danger':
        return 'bg-red-600 hover:bg-red-700 focus:ring-red-500/50 text-white';
      case 'warning':
        return 'bg-yellow-600 hover:bg-yellow-700 focus:ring-yellow-500/50 text-white';
      case 'info':
        return 'bg-blue-600 hover:bg-blue-700 focus:ring-blue-500/50 text-white';
      default:
        return 'bg-red-600 hover:bg-red-700 focus:ring-red-500/50 text-white';
    }
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      size="sm"
      closeOnOverlayClick={!isLoading}
      closeOnEscape={!isLoading}
      showCloseButton={false}
    >
      <div className="p-6 text-center">
        {getIcon()}
        
        <h3 className="text-lg font-semibold text-white mb-2">
          {title}
        </h3>
        
        <p className="text-gray-300 mb-6 leading-relaxed">
          {message}
        </p>
        
        <div className="flex space-x-3 justify-center">
          <button
            onClick={onClose}
            disabled={isLoading}
            className="
              px-4 py-2 text-sm font-medium text-gray-300 
              bg-gray-800 border border-gray-600 rounded-lg
              hover:bg-gray-700 hover:text-white hover:border-gray-500
              focus:outline-none focus:ring-2 focus:ring-gray-500/50
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200
            "
          >
            {cancelText}
          </button>
          
          <button
            onClick={handleConfirm}
            disabled={isLoading}
            className={`
              px-4 py-2 text-sm font-medium rounded-lg
              focus:outline-none focus:ring-2 
              disabled:opacity-50 disabled:cursor-not-allowed
              transition-all duration-200 min-w-[100px]
              ${getConfirmButtonStyles()}
            `}
          >
            {isLoading ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Удаление...
              </div>
            ) : (
              confirmText
            )}
          </button>
        </div>
      </div>
    </Modal>
  );
} 