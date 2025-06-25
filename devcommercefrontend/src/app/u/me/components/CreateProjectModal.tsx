'use client';

import { useState } from 'react';

interface CreateProjectModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (projectData: any) => void;
  isLoading?: boolean;
}

export default function CreateProjectModal({ isOpen, onClose, onSubmit, isLoading = false }: CreateProjectModalProps) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    github_link: '',
    project_public_link: '',
    status: 'public',
    technologies: [] as string[],
    project_photo: null as File | null
  });

  const [newTech, setNewTech] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    

    if (!formData.title.trim()) {
      alert('Введите название проекта');
      return;
    }
    
    if (!formData.description.trim()) {
      alert('Введите описание проекта');
      return;
    }
    
    if (!formData.project_public_link.trim()) {
      alert('Введите публичную ссылку на проект');
      return;
    }
    
    
    if (!formData.project_public_link.startsWith('https://')) {
      alert('Публичная ссылка должна начинаться с https://');
      return;
    }

    onSubmit(formData);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null;
    setFormData(prev => ({
      ...prev,
      project_photo: file
    }));
  };

  const addTechnology = () => {
    if (newTech.trim() && !formData.technologies.includes(newTech.trim())) {
      setFormData(prev => ({
        ...prev,
        technologies: [...prev.technologies, newTech.trim()]
      }));
      setNewTech('');
    }
  };

  const removeTechnology = (tech: string) => {
    setFormData(prev => ({
      ...prev,
      technologies: prev.technologies.filter(t => t !== tech)
    }));
  };

  const resetForm = () => {
    setFormData({
      title: '',
      description: '',
      github_link: '',
      project_public_link: '',
      status: 'public',
      technologies: [],
      project_photo: null
    });
    setNewTech('');
  };

  const handleClose = () => {
    resetForm();
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center">
      {/* Backdrop */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Modal */}
      <div className="relative w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
        <div className="bg-gray-900 border border-gray-700 rounded-xl shadow-2xl">
          {/* Header */}
          <div className="flex items-center justify-between p-6 border-b border-gray-700">
            <h2 className="text-2xl font-bold text-white">Создать новый проект</h2>
            <button
              onClick={handleClose}
              className="text-gray-400 hover:text-white transition-colors"
              disabled={isLoading}
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
              </svg>
            </button>
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} className="p-6 space-y-6">
            {/* Название проекта */}
            <div>
              <label className="block text-white font-medium mb-2">
                Название проекта *
              </label>
              <input
                type="text"
                name="title"
                value={formData.title}
                onChange={handleInputChange}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors"
                placeholder="Введите название проекта"
                disabled={isLoading}
                required
              />
            </div>

            {/* Описание */}
            <div>
              <label className="block text-white font-medium mb-2">
                Описание проекта *
              </label>
              <textarea
                name="description"
                value={formData.description}
                onChange={handleInputChange}
                rows={4}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors resize-none"
                placeholder="Опишите ваш проект"
                disabled={isLoading}
                required
              />
            </div>

            {/* Публичная ссылка */}
            <div>
              <label className="block text-white font-medium mb-2">
                Публичная ссылка на проект *
              </label>
              <input
                type="url"
                name="project_public_link"
                value={formData.project_public_link}
                onChange={handleInputChange}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors"
                placeholder="https://example.com"
                disabled={isLoading}
                required
              />
            </div>

            {/* GitHub ссылка */}
            <div>
              <label className="block text-white font-medium mb-2">
                GitHub ссылка (опционально)
              </label>
              <input
                type="url"
                name="github_link"
                value={formData.github_link}
                onChange={handleInputChange}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors"
                placeholder="https://github.com/username/project"
                disabled={isLoading}
              />
            </div>

            {/* Статус проекта */}
            <div>
              <label className="block text-white font-medium mb-2">
                Статус проекта
              </label>
              <select
                name="status"
                value={formData.status}
                onChange={handleInputChange}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors"
                disabled={isLoading}
              >
                <option value="public">Публичный - виден всем</option>
                <option value="profile_only">Только в профиле - виден в вашем профиле</option>
                <option value="private">Приватный - виден только вам</option>
              </select>
            </div>

            {/* Изображение проекта */}
            <div>
              <label className="block text-white font-medium mb-2">
                Изображение проекта
              </label>
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="w-full bg-gray-800 border border-gray-600 text-white px-4 py-3 rounded-lg focus:border-white focus:outline-none transition-colors file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-white file:text-black file:font-medium hover:file:bg-gray-100"
                disabled={isLoading}
              />
            </div>

            {/* Технологии */}
            <div>
              <label className="block text-white font-medium mb-2">
                Технологии
              </label>
              <div className="flex space-x-2 mb-3">
                <input
                  type="text"
                  value={newTech}
                  onChange={(e) => setNewTech(e.target.value)}
                  className="flex-1 bg-gray-800 border border-gray-600 text-white px-4 py-2 rounded-lg focus:border-white focus:outline-none transition-colors"
                  placeholder="Добавить технологию"
                  disabled={isLoading}
                  onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTechnology())}
                />
                <button
                  type="button"
                  onClick={addTechnology}
                  className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                  disabled={isLoading}
                >
                  Добавить
                </button>
              </div>
              
              {/* Список технологий */}
              <div className="flex flex-wrap gap-2">
                {formData.technologies.map((tech, index) => (
                  <span
                    key={index}
                    className="bg-gray-800 text-white px-3 py-1 rounded-lg text-sm flex items-center space-x-2 border border-gray-600"
                  >
                    <span>{tech}</span>
                    <button
                      type="button"
                      onClick={() => removeTechnology(tech)}
                      className="text-gray-400 hover:text-white transition-colors"
                      disabled={isLoading}
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </span>
                ))}
              </div>
            </div>

            {/* Кнопки */}
            <div className="flex space-x-4 pt-4">
              <button
                type="button"
                onClick={handleClose}
                className="flex-1 bg-gray-800 text-white py-3 px-6 rounded-lg font-medium border border-gray-600 hover:bg-gray-700 transition-colors"
                disabled={isLoading}
              >
                Отмена
              </button>
              <button
                type="submit"
                className="flex-1 bg-white text-black py-3 px-6 rounded-lg font-medium hover:bg-gray-100 transition-colors disabled:opacity-50"
                disabled={isLoading}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center">
                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-black" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    Создание...
                  </span>
                ) : (
                  'Создать проект'
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
} 