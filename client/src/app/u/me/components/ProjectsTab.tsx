'use client';

import { useState, useEffect } from 'react';
import { projectsAPI } from '../../../../api/projects/api';
import CreateProjectModal from './CreateProjectModal';
import SimpleLoader from '@/components/simple-loader';
export default function ProjectsTab() {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');

  const loadProjects = async () => {
    try {
      setLoading(true);
      setError('');
      
      const response = await projectsAPI.getMyProjects(currentPage, 12, statusFilter);
      setProjects(response.results);
      setTotalPages(response.total_pages);
    } catch (err: any) {
      setError(err?.message || 'Ошибка при загрузке проектов');
    } finally {
      setLoading(false);
    }
  };
  const handleCreateProject = async (projectData: any) => {
    try {
      setIsCreating(true);
      await projectsAPI.createProject(projectData);
      setIsCreateModalOpen(false);
      loadProjects();
    } catch (err: any) {
      alert(err?.message || 'Ошибка при создании проекта');
    } finally {
      setIsCreating(false);
    }
  };
  const handleDeleteProject = async (projectId: string, projectTitle: string) => {
    if (!confirm(`Вы уверены, что хотите удалить проект "${projectTitle}"?`)) {
      return;
    }

    try {
      await projectsAPI.deleteProject(projectId);
      loadProjects();
    } catch (err: any) {
      alert(err?.message || 'Ошибка при удалении проекта');
    }
  };
  const handleStatusChange = async (projectId: string, newStatus: string) => {
    try {
      await projectsAPI.updateProjectStatus(projectId, newStatus);
      loadProjects();
    } catch (err: any) {
      alert(err?.message || 'Ошибка при изменении статуса');
    }
  };

  useEffect(() => {
    loadProjects();
  }, [currentPage, statusFilter]);
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'public': return 'text-green-400';
      case 'profile_only': return 'text-yellow-400';
      case 'private': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getStatusName = (status: string) => {
    switch (status) {
      case 'public': return 'Публичный';
      case 'profile_only': return 'В профиле';
      case 'private': return 'Приватный';
      default: return status;
    }
  };

  const ProjectCard = ({ project }: { project: any }) => {
    const formatDate = (dateString: string) => {
      return new Date(dateString).toLocaleDateString('ru-RU', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
      });
    };

    return (
      <div className="bg-black border border-gray-700 rounded-xl p-8 hover:border-gray-600 transition-all duration-300 shadow-2xl">
        <div className="flex gap-6">
          <div className="flex-shrink-0">
            {project.project_photo ? (
              <img
                src={project.project_photo}                alt={project.title}
                className="w-32 h-32 object-cover rounded-lg border border-gray-700"
              />
            ) : (
              <div className="w-32 h-32 bg-gray-800 rounded-lg border border-gray-700 flex items-center justify-center">
                <svg className="w-12 h-12 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4 3a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V5a2 2 0 00-2-2H4zm12 12H4l4-8 3 6 2-4 3 6z" clipRule="evenodd" />
                </svg>
              </div>
            )}
          </div>

          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-4">
              <div className="flex-1 min-w-0">
                <h3 className="text-2xl font-bold text-white hover:text-blue-400 cursor-pointer mb-2 truncate">
                  {project.title}
                </h3>
                <div className="flex items-center space-x-3 mb-3">
                  <span className={`px-3 py-1 rounded-full text-sm font-medium border ${getStatusColor(project.status)} ${
                    project.status === 'public' ? 'border-green-400 bg-green-400/10' :
                    project.status === 'profile_only' ? 'border-yellow-400 bg-yellow-400/10' :
                    'border-red-400 bg-red-400/10'
                  }`}>
                    {getStatusName(project.status)}
                  </span>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => window.open(project.project_public_link, '_blank')}
                      className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                      title="Открыть проект"
                    >
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path d="M11 3a1 1 0 100 2h2.586l-6.293 6.293a1 1 0 101.414 1.414L15 6.414V9a1 1 0 102 0V4a1 1 0 00-1-1h-5z" />
                        <path d="M5 5a2 2 0 00-2 2v8a2 2 0 002 2h8a2 2 0 002-2v-3a1 1 0 10-2 0v3H5V7h3a1 1 0 000-2H5z" />
                      </svg>
                    </button>
                    
                    {project.github_link && (
                      <button
                        onClick={() => window.open(project.github_link, '_blank')}
                        className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors"
                        title="GitHub"
                      >
                        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M10 0C4.477 0 0 4.484 0 10.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0110 4.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.203 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.942.359.31.678.921.678 1.856 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0020 10.017C20 4.484 15.522 0 10 0z" clipRule="evenodd" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              </div>
              <div className="relative group">
                <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-800 rounded-lg transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>
                
                <div className="absolute right-0 top-10 bg-gray-800 border border-gray-600 rounded-lg shadow-xl opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-20 min-w-[200px]">
                  <div className="py-2">
                    <div className="px-4 py-2 text-xs text-gray-400 border-b border-gray-600">
                      Изменить статус:
                    </div>
                                          <select
                        value={project.status}
                        onChange={(e) => handleStatusChange(project.id, e.target.value)}
                        className="w-full bg-gray-700 text-white text-sm px-4 py-2 hover:bg-gray-600 transition-colors border-0 outline-0"
                      >
                        <option value="public"> Публичный</option>
                        <option value="profile_only"> В профиле</option>
                        <option value="private"> Приватный</option>
                      </select>
                    <hr className="border-gray-600" />
                                          <button
                        onClick={() => handleDeleteProject(project.id, project.title)}
                        className="w-full text-left px-4 py-2 text-sm text-red-400 hover:bg-gray-700 transition-colors"
                      >
                        🗑️ Удалить проект
                      </button>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-gray-300 mb-4 line-clamp-2 leading-relaxed">
              {project.description}
            </p>
            <div className="flex flex-wrap gap-2 mb-4">
              {project.technologies?.map((tech: string, index: number) => (
                <span key={index} className="bg-gray-800 text-gray-200 px-3 py-1 rounded-full text-sm border border-gray-700 hover:border-gray-600 transition-colors">
                  {tech}
                </span>
              ))}
            </div>
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-6">
                <div className="flex items-center space-x-2 text-gray-400">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                  <span className="font-medium">{project.likes}</span>
                </div>
                
                <div className="flex items-center space-x-2 text-gray-400">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                    <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
                  </svg>
                  <span className="font-medium">{project.views}</span>
                </div>
              </div>
              
              <span className="text-gray-400 text-sm">
                Обновлен {formatDate(project.updated_at)}
              </span>
            </div>
          </div>
        </div>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-black flex items-center justify-center">
      <SimpleLoader text="Загрузка проектов..." fullScreen={true} />
    </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-white mb-2">Проекты</h1>
          <p className="text-gray-400">Ваши репозитории и проекты</p>
        </div>
        <button 
          onClick={() => setIsCreateModalOpen(true)}
          className="bg-white text-black px-4 py-2 rounded-lg font-medium hover:bg-gray-100 transition-colors"
        >
          Новый проект
        </button>
      </div>
      <div className="flex items-center space-x-4 mb-8">
        <div className="flex items-center space-x-2">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="bg-gray-900 border border-gray-800 text-white px-4 py-2 rounded-lg focus:border-gray-600 focus:outline-none"
          >
            <option value="">Все статусы</option>
            <option value="public">Публичные</option>
            <option value="profile_only">В профиле</option>
            <option value="private">Приватные</option>
          </select>
        </div>
      </div>
      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-300 px-4 py-3 rounded-lg mb-6">
          {error}
          <button 
            onClick={loadProjects}
            className="ml-4 text-red-400 hover:text-red-300 underline"
          >
            Попробовать снова
          </button>
        </div>
      )}
      {projects.length > 0 ? (
        <>
          <div className="grid grid-cols-1 gap-8">
            {projects.map((project: any) => (
              <ProjectCard key={project.id} project={project} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex justify-center mt-8 space-x-2">
              <button
                onClick={() => setCurrentPage(prev => Math.max(prev - 1, 1))}
                disabled={currentPage === 1}
                className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Назад
              </button>
              <span className="bg-gray-900 text-white px-4 py-2 rounded-lg border border-gray-700">
                {currentPage} из {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(prev => Math.min(prev + 1, totalPages))}
                disabled={currentPage === totalPages}
                className="bg-gray-800 text-white px-4 py-2 rounded-lg border border-gray-700 hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                Далее
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-16">
          <svg className="w-24 h-24 mx-auto text-gray-600 mb-6" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H6.414l2.293 2.293a1 1 0 11-1.414 1.414L5 6.414V8a1 1 0 11-2 0V4zm9 1a1 1 0 010-2h4a1 1 0 011 1v4a1 1 0 11-2 0V6.414l-2.293 2.293a1 1 0 11-1.414-1.414L13.586 5H12zm-9 7a1 1 0 112 0v1.586l2.293-2.293a1 1 0 111.414 1.414L6.414 15H8a1 1 0 110 2H4a1 1 0 01-1-1v-4zm13-1a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 110-2h1.586l-2.293-2.293a1 1 0 111.414-1.414L15.586 13V12a1 1 0 011-1z" clipRule="evenodd" />
          </svg>
          <h3 className="text-xl font-bold text-white mb-2">Пока нет проектов</h3>
          <p className="text-gray-400 mb-6 max-w-md mx-auto">
            Создайте свой первый проект, чтобы начать отслеживать вашу работу и делиться кодом с сообществом.
          </p>
          <button 
            onClick={() => setIsCreateModalOpen(true)}
            className="bg-white text-black px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
          >
            Создать первый проект
          </button>
        </div>
      )}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
        isLoading={isCreating}
      />
    </div>
  );
} 