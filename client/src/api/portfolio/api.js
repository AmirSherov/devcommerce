const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api';

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('access_token');
  return token ? { 'Authorization': `Bearer ${token}` } : {};
};

// Helper function to handle API responses
const handleResponse = async (response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || errorData.message || `HTTP error! status: ${response.status}`);
  }
  return await response.json();
};

export const portfolioAPI = {
  
  // Get public portfolios with pagination and filters
  getPortfolios: async (params = {}) => {
    const queryParams = new URLSearchParams();
    
    if (params.page) queryParams.append('page', params.page);
    if (params.search) queryParams.append('search', params.search);
    if (params.tags) queryParams.append('tags', params.tags);
    if (params.order_by) queryParams.append('order_by', params.order_by);
    
    const response = await fetch(`${API_BASE_URL}/portfolio/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return await handleResponse(response);
  },

  // Get current user's portfolios
  getMyPortfolios: async () => {
    const response = await fetch(`${API_BASE_URL}/portfolio/me/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Get portfolio by ID
  getPortfolio: async (portfolioId) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/${portfolioId}/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Create new portfolio
  createPortfolio: async (portfolioData) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/create/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(portfolioData),
    });
    
    return await handleResponse(response);
  },

  // Update portfolio
  updatePortfolio: async (portfolioId, portfolioData) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/${portfolioId}/update/`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(portfolioData),
    });
    
    return await handleResponse(response);
  },

  // Autosave portfolio code (for live editing)
  autosavePortfolio: async (portfolioId, codeData) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/${portfolioId}/autosave/`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
      body: JSON.stringify(codeData),
    });
    
    return await handleResponse(response);
  },

  // Delete portfolio
  deletePortfolio: async (portfolioId) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/${portfolioId}/delete/`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Toggle like on portfolio
  togglePortfolioLike: async (portfolioId) => {
    const response = await fetch(`${API_BASE_URL}/portfolio/${portfolioId}/like/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Get user's portfolios by username
  getUserPortfolios: async (username, params = {}) => {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page);
    
    const response = await fetch(`${API_BASE_URL}/portfolio/user/${username}/?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return await handleResponse(response);
  },

  // Get current user's portfolio statistics
  getMyPortfolioStats: async () => {
    const response = await fetch(`${API_BASE_URL}/portfolio/stats/me/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...getAuthHeaders(),
      },
    });
    
    return await handleResponse(response);
  },

  // Get global portfolio statistics
  getGlobalPortfolioStats: async () => {
    const response = await fetch(`${API_BASE_URL}/portfolio/stats/global/`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return await handleResponse(response);
  },

}; 