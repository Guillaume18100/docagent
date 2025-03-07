import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API base URLs from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const DOCUMENTS_API_URL = import.meta.env.VITE_DOCUMENTS_API_URL || `${API_BASE_URL}/documents/`;
const NLP_API_URL = import.meta.env.VITE_NLP_API_URL || `${API_BASE_URL}/nlp/`;
const GENERATE_API_URL = import.meta.env.VITE_GENERATE_API_URL || `${API_BASE_URL}/generate/`;
const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000/media/';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
});

// Add request interceptor for authentication
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('docautomation_access_token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Document API methods
export const documentApi = {
  getDocuments: async () => {
    try {
      const response = await apiClient.get(`${DOCUMENTS_API_URL}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching documents:', error);
      throw error;
    }
  },

  getDocument: async (id: string) => {
    try {
      const response = await apiClient.get(`${DOCUMENTS_API_URL}${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching document ${id}:`, error);
      throw error;
    }
  },

  uploadDocument: async (file: File | FormData) => {
    try {
      console.log("Uploading document via Axios");
      
      // Create FormData if file is passed directly
      const formData = file instanceof FormData ? file : new FormData();
      
      // Add file to FormData if not already there
      if (!(file instanceof FormData)) {
        formData.append('file', file);
        // Also add a title field which is required by the backend
        formData.append('title', file.name);
      }
      
      // Use the public upload endpoint for more reliable uploads
      const uploadUrl = `${DOCUMENTS_API_URL}public-upload/`;
      console.log('Upload URL:', uploadUrl);
      
      // Log the full URL for debugging
      console.log('Full URL:', new URL(uploadUrl, window.location.origin).toString());
      
      // Use Axios directly with FormData
      const response = await axios.post(uploadUrl, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          // Don't set any other headers that might interfere with the boundary
        },
        withCredentials: true,
      });
      
      console.log('Upload response:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  },

  getExtractedText: async (id: string) => {
    try {
      const response = await apiClient.get(`${DOCUMENTS_API_URL}${id}/extracted_text/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching extracted text for document ${id}:`, error);
      throw error;
    }
  },

  reprocessDocument: async (id: string) => {
    try {
      const response = await apiClient.post(`${DOCUMENTS_API_URL}${id}/reprocess/`);
      return response.data;
    } catch (error) {
      console.error(`Error reprocessing document ${id}:`, error);
      throw error;
    }
  },

  downloadDocument: async (id: string) => {
    try {
      const response = await apiClient.get(`${DOCUMENTS_API_URL}${id}/download/`, {
        responseType: 'blob'
      });
      return response.data;
    } catch (error) {
      console.error(`Error downloading document ${id}:`, error);
      throw error;
    }
  },

  getDocumentPreview: async (id: string) => {
    try {
      const response = await apiClient.get(`${DOCUMENTS_API_URL}${id}/preview/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching preview for document ${id}:`, error);
      throw error;
    }
  },
};

// Authentication functions
export const authApi = {
  login: async (username: string, password: string) => {
    try {
      const response = await apiClient.post(`/token/`, { username, password });
      const { access, refresh } = response.data;
      
      // Store tokens
      localStorage.setItem('docautomation_access_token', access);
      localStorage.setItem('docautomation_refresh_token', refresh);
      
      return true;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    }
  },
  
  logout: () => {
    localStorage.removeItem('docautomation_access_token');
    localStorage.removeItem('docautomation_refresh_token');
  },
  
  isAuthenticated: () => {
    return !!localStorage.getItem('docautomation_access_token');
  },
  
  register: async (username: string, email: string, password: string) => {
    try {
      const response = await apiClient.post(`/register/`, {
        username,
        email,
        password
      });
      return response.data;
    } catch (error) {
      console.error('Registration error:', error);
      throw error;
    }
  }
};

// NLP API methods
export const nlpApi = {
  analyzeQuery: async (data: { query_text: string; document_ids?: string[] }) => {
    try {
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, data);
      return response.data;
    } catch (error) {
      console.error('Error analyzing query:', error);
      throw error;
    }
  },

  getConversations: async () => {
    try {
      const response = await apiClient.get(`${NLP_API_URL}conversation/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  getConversation: async (id: string) => {
    try {
      const response = await apiClient.get(`${NLP_API_URL}conversation/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching conversation ${id}:`, error);
      throw error;
    }
  },

  createConversation: async (data: { title: string }) => {
    try {
      const response = await apiClient.post(`${NLP_API_URL}conversation/`, data);
      return response.data;
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  addMessage: async (conversationId: string, data: { role: string; content: string }) => {
    try {
      const response = await apiClient.post(`${NLP_API_URL}conversation/${conversationId}/add_message/`, data);
      return response.data;
    } catch (error) {
      console.error(`Error adding message to conversation ${conversationId}:`, error);
      throw error;
    }
  },

  // Additional methods for compatibility with chatService usage
  getChatHistory: async (documentId: string) => {
    try {
      // Map to the new API - get conversations related to a document
      const response = await apiClient.get(`${NLP_API_URL}conversation/`, {
        params: { document_id: documentId }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching chat history for document ${documentId}:`, error);
      return []; // Return empty array as fallback
    }
  },
  
  sendMessage: async (documentId: string, message: string) => {
    try {
      // Map to the new API - create a new user query or add to conversation
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, {
        query_text: message,
        document_ids: [documentId]
      });
      return response.data;
    } catch (error) {
      console.error(`Error sending message for document ${documentId}:`, error);
      throw error;
    }
  }
};

// Document Generation API methods
export const generateApi = {
  getTemplates: async () => {
    try {
      const response = await apiClient.get(`${GENERATE_API_URL}templates/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching templates:', error);
      throw error;
    }
  },

  getTemplate: async (id: string) => {
    try {
      const response = await apiClient.get(`${GENERATE_API_URL}templates/${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching template ${id}:`, error);
      throw error;
    }
  },

  getGeneratedDocuments: async () => {
    try {
      const response = await apiClient.get(`${GENERATE_API_URL}`);
      return response.data;
    } catch (error) {
      console.error('Error fetching generated documents:', error);
      throw error;
    }
  },

  getGeneratedDocument: async (id: string) => {
    try {
      const response = await apiClient.get(`${GENERATE_API_URL}${id}/`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching generated document ${id}:`, error);
      throw error;
    }
  },

  generateDocument: async (data: { 
    title: string; 
    prompt: string; 
    output_format?: string; 
    template_id?: string; 
    document_ids?: string[];
  }) => {
    try {
      const response = await apiClient.post(`${GENERATE_API_URL}`, data);
      return response.data;
    } catch (error) {
      console.error('Error generating document:', error);
      throw error;
    }
  },

  regenerateDocument: async (id: string) => {
    try {
      const response = await apiClient.post(`${GENERATE_API_URL}${id}/regenerate/`);
      return response.data;
    } catch (error) {
      console.error(`Error regenerating document ${id}:`, error);
      throw error;
    }
  },

  getDownloadUrl: (id: string) => `${GENERATE_API_URL}${id}/download/`,
};

// Helper utility
export const getMediaUrl = (path: string) => {
  if (path.startsWith('http')) {
    return path;
  }
  return `${MEDIA_URL}${path.replace(/^\//, '')}`;
};

// For backward compatibility with existing code
export const documentService = documentApi;
export const chatService = nlpApi;

export default {
  documentApi,
  nlpApi,
  generateApi,
  authApi,
  getMediaUrl,
  // Include these for backward compatibility
  documentService,
  chatService,
};
