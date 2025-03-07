/**
 * API Service for communicating with the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const DOCUMENTS_API_URL = import.meta.env.VITE_DOCUMENTS_API_URL || `${API_BASE_URL}/documents/`;
const NLP_API_URL = import.meta.env.VITE_NLP_API_URL || `${API_BASE_URL}/nlp/`;
const GENERATE_API_URL = import.meta.env.VITE_GENERATE_API_URL || `${API_BASE_URL}/generate/`;
const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000/media/';
const AUTH_TOKEN_URL = `${API_BASE_URL}/token/`;
const AUTH_REFRESH_URL = `${API_BASE_URL}/token/refresh/`;

// Token storage keys
const ACCESS_TOKEN_KEY = 'docautomation_access_token';
const REFRESH_TOKEN_KEY = 'docautomation_refresh_token';

/**
 * Get the stored access token
 */
const getAccessToken = (): string | null => {
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

/**
 * Get the stored refresh token
 */
const getRefreshToken = (): string | null => {
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

/**
 * Store authentication tokens
 */
const storeTokens = (accessToken: string, refreshToken: string): void => {
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

/**
 * Clear stored tokens
 */
const clearTokens = (): void => {
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
};

/**
 * Default fetch options for API requests
 */
const defaultOptions: RequestInit = {
  headers: {
    'Content-Type': 'application/json',
  },
  credentials: 'include',
};

/**
 * Add authorization header if access token exists
 */
const getAuthHeaders = (): HeadersInit => {
  const accessToken = getAccessToken();
  if (accessToken) {
    return {
      'Authorization': `Bearer ${accessToken}`,
    };
  }
  return {};
};

/**
 * Refresh the access token using the refresh token
 */
const refreshAccessToken = async (): Promise<boolean> => {
  const refreshToken = getRefreshToken();
  if (!refreshToken) {
    clearTokens();
    return false;
  }

  try {
    const response = await fetch(AUTH_REFRESH_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ refresh: refreshToken }),
    });

    if (!response.ok) {
      clearTokens();
      return false;
    }

    const data = await response.json();
    localStorage.setItem(ACCESS_TOKEN_KEY, data.access);
    return true;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    clearTokens();
    return false;
  }
};

/**
 * Login function
 */
export const login = async (username: string, password: string): Promise<boolean> => {
  try {
    const response = await fetch(AUTH_TOKEN_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const { access, refresh } = await response.json();
    storeTokens(access, refresh);
    return true;
  } catch (error) {
    console.error('Login failed:', error);
    throw error;
  }
};

/**
 * Logout function
 */
export const logout = (): void => {
  clearTokens();
};

/**
 * Check if user is authenticated
 */
export const isAuthenticated = (): boolean => {
  return !!getAccessToken();
};

/**
 * Generic API fetch function with error handling and token refresh
 */
const apiFetch = async <T>(
  url: string, 
  options: RequestInit = {}
): Promise<T> => {
  // Add auth headers to the request
  const authHeaders = getAuthHeaders();
  
  try {
    // First attempt with current access token
    const response = await fetch(url, {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...authHeaders,
        ...options.headers,
      },
    });

    // If unauthorized and we have a refresh token, try to refresh and retry
    if (response.status === 401 && getRefreshToken()) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry with new access token
        const newAuthHeaders = getAuthHeaders();
        const retryResponse = await fetch(url, {
          ...defaultOptions,
          ...options,
          headers: {
            ...defaultOptions.headers,
            ...newAuthHeaders,
            ...options.headers,
          },
        });

        if (!retryResponse.ok) {
          const error = await retryResponse.json().catch(() => ({
            message: retryResponse.statusText,
          }));
          throw new Error(error.message || 'An error occurred');
        }

        // For empty responses or 204 No Content
        if (retryResponse.status === 204 || retryResponse.headers.get('Content-Length') === '0') {
          return {} as T;
        }

        return await retryResponse.json();
      } else {
        // If refresh failed, clear tokens and throw error
        clearTokens();
        throw new Error('Session expired. Please login again.');
      }
    }

    if (!response.ok) {
      const error = await response.json().catch(() => ({
        message: response.statusText,
      }));
      throw new Error(error.message || 'An error occurred');
    }

    // For empty responses or 204 No Content
    if (response.status === 204 || response.headers.get('Content-Length') === '0') {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    console.error('API request failed:', error);
    throw error;
  }
};

/**
 * Document API endpoints
 */
export const documentApi = {
  /**
   * Get list of all documents
   */
  getDocuments: () => apiFetch<any[]>(`${DOCUMENTS_API_URL}`),

  /**
   * Get a specific document by ID
   */
  getDocument: (id: string) => apiFetch<any>(`${DOCUMENTS_API_URL}${id}/`),

  /**
   * Upload a document
   */
  uploadDocument: async (file: File | FormData) => {
    try {
      console.log('Uploading to URL:', `${DOCUMENTS_API_URL}upload/`);
      
      // Create FormData if file is passed directly
      const formData = file instanceof FormData ? file : new FormData();
      
      // Add file to FormData if not already there
      if (!(file instanceof FormData)) {
        formData.append('file', file);
      }
      
      // Handle the upload directly with fetch for better control
      const response = await fetch(`${DOCUMENTS_API_URL}upload/`, {
        method: 'POST',
        body: formData,
        // No Content-Type header - browser will set it with boundary
        headers: {
          ...getAuthHeaders()
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error('Upload error response:', errorText);
        try {
          const errorJson = JSON.parse(errorText);
          throw new Error(errorJson.detail || errorJson.error || 'Upload failed');
        } catch (e) {
          throw new Error(`Upload failed: ${response.status} ${response.statusText}`);
        }
      }

      return await response.json();
    } catch (error) {
      console.error('Upload error:', error);
      throw error;
    }
  },

  /**
   * Get extracted text from a document
   */
  getExtractedText: (id: string) => apiFetch<any>(`${DOCUMENTS_API_URL}${id}/extracted_text/`),

  /**
   * Reprocess a document
   */
  reprocessDocument: (id: string) => apiFetch<any>(`${DOCUMENTS_API_URL}${id}/reprocess/`, {
    method: 'POST',
  }),
};

/**
 * NLP API endpoints
 */
export const nlpApi = {
  /**
   * Analyze a user query
   */
  analyzeQuery: (data: { query_text: string; document_ids?: string[] }) => {
    return apiFetch<any>(`${NLP_API_URL}analyze/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Get all conversations
   */
  getConversations: () => apiFetch<any[]>(`${NLP_API_URL}conversation/`),

  /**
   * Get a specific conversation by ID
   */
  getConversation: (id: string) => apiFetch<any>(`${NLP_API_URL}conversation/${id}/`),

  /**
   * Create a new conversation
   */
  createConversation: (data: { title: string }) => {
    return apiFetch<any>(`${NLP_API_URL}conversation/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Add a message to a conversation
   */
  addMessage: (conversationId: string, data: { role: string; content: string }) => {
    return apiFetch<any>(`${NLP_API_URL}conversation/${conversationId}/add_message/`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
};

/**
 * Document Generation API endpoints
 */
export const generateApi = {
  /**
   * Get all document templates
   */
  getTemplates: () => apiFetch<any[]>(`${GENERATE_API_URL}templates/`),

  /**
   * Get a specific document template by ID
   */
  getTemplate: (id: string) => apiFetch<any>(`${GENERATE_API_URL}templates/${id}/`),

  /**
   * Get all generated documents
   */
  getGeneratedDocuments: () => apiFetch<any[]>(`${GENERATE_API_URL}`),

  /**
   * Get a specific generated document by ID
   */
  getGeneratedDocument: (id: string) => apiFetch<any>(`${GENERATE_API_URL}${id}/`),

  /**
   * Generate a document
   */
  generateDocument: (data: { 
    title: string; 
    prompt: string; 
    template_id?: string; 
    document_ids?: string[];
    parameters?: Record<string, any>; 
  }) => {
    return apiFetch<any>(`${GENERATE_API_URL}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  /**
   * Regenerate a document
   */
  regenerateDocument: (id: string) => apiFetch<any>(`${GENERATE_API_URL}${id}/regenerate/`, {
    method: 'POST',
  }),

  /**
   * Get the download URL for a generated document
   */
  getDownloadUrl: (id: string) => `${GENERATE_API_URL}${id}/download/`,
};

/**
 * Helper to get media file URL
 */
export const getMediaUrl = (path: string) => {
  // If path is already a full URL, return it as is
  if (path.startsWith('http')) {
    return path;
  }
  // Otherwise, prepend the media URL
  return `${MEDIA_URL}${path.replace(/^\//, '')}`;
};

/**
 * Register a new user
 */
export const register = async (
  username: string, 
  email: string, 
  password: string
): Promise<any> => {
  try {
    const response = await fetch(`${API_BASE_URL}/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.error || 'Registration failed');
    }

    return await response.json();
  } catch (error) {
    console.error('Registration failed:', error);
    throw error;
  }
};

export default {
  documentApi,
  nlpApi,
  generateApi,
  getMediaUrl,
  login,
  logout,
  isAuthenticated,
  register,
}; 