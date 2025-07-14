import { getSessionHeaders } from '../../lib/auth-utils';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const getAuthToken = () => {
  if (typeof window !== 'undefined') {
    return localStorage.getItem('access_token');
  }
  return null;
};

const getAuthHeaders = () => {
  const token = getAuthToken();
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

const getAuthHeadersFormData = () => {
  const token = getAuthToken();
  return {
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

export const projectsAPI = {
  getPublicProjects: async (page = 1, pageSize = 12, search = '', technologies = '') => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(search && { search }),
      ...(technologies && { technologies })
    });

    const response = await fetch(`${API_BASE_URL}/projects/?${params}`);
    
    if (!response.ok) {
      throw new Error('Ошибка при получении проектов');
    }
    
    return response.json();
  },
  getMyProjects: async (page = 1, pageSize = 12, status = '') => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString(),
      ...(status && { status })
    });

    const response = await fetch(`${API_BASE_URL}/projects/me/?${params}`, {
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
        ...getSessionHeaders(),
      },
    });
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        throw new Error('Необходима авторизация');
      }
      throw new Error('Ошибка при получении ваших проектов');
    }
    
    return response.json();
  },
  createProject: async (projectData) => {
    const formData = new FormData();
    formData.append('title', projectData.title);
    formData.append('description', projectData.description);
    formData.append('project_public_link', projectData.project_public_link);
    formData.append('status', projectData.status);
    formData.append('technologies', JSON.stringify(projectData.technologies));
    if (projectData.github_link) {
      formData.append('github_link', projectData.github_link);
    }
    
    if (projectData.project_photo) {
      formData.append('project_photo', projectData.project_photo);
    }

    const response = await fetch(`${API_BASE_URL}/projects/create/me/`, {
      method: 'POST',
      headers: getAuthHeadersFormData(),
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Ошибка при создании проекта');
    }
    
    return response.json();
  },

  updateProject: async (projectId, projectData) => {
    const formData = new FormData();
    if (projectData.title) formData.append('title', projectData.title);
    if (projectData.description) formData.append('description', projectData.description);
    if (projectData.project_public_link) formData.append('project_public_link', projectData.project_public_link);
    if (projectData.github_link) formData.append('github_link', projectData.github_link);
    if (projectData.technologies) formData.append('technologies', JSON.stringify(projectData.technologies));
    if (projectData.project_photo) formData.append('project_photo', projectData.project_photo);

    const response = await fetch(`${API_BASE_URL}/projects/me/${projectId}/`, {
      method: 'PATCH',
      headers: getAuthHeadersFormData(),
      body: formData
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Ошибка при обновлении проекта');
    }
    
    return response.json();
  },
  deleteProject: async (projectId) => {
    const response = await fetch(`${API_BASE_URL}/projects/delete/me/${projectId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Ошибка при удалении проекта');
    }
    
    return response.json();
  },
  updateProjectStatus: async (projectId, status) => {
    const response = await fetch(`${API_BASE_URL}/projects/status/me/${projectId}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ status })
    });
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.error || 'Ошибка при изменении статуса проекта');
    }
    
    return response.json();
  },
  getProjectBySlug: async (slug) => {
    const response = await fetch(`${API_BASE_URL}/projects/${slug}/`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Проект не найден');
    }
    
    return response.json();
  },
  getUserProjects: async (username, page = 1, pageSize = 12) => {
    const params = new URLSearchParams({
      page: page.toString(),
      page_size: pageSize.toString()
    });

    const response = await fetch(`${API_BASE_URL}/projects/user/${username}/?${params}`, {
      headers: getAuthHeaders()
    });
    
    if (!response.ok) {
      throw new Error('Ошибка при получении проектов пользователя');
    }
    
    return response.json();
  }
}; 