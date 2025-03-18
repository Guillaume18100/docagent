import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';

// API base URLs from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';
const DOCUMENTS_API_URL = import.meta.env.VITE_DOCUMENTS_API_URL || `${API_BASE_URL}/documents/`;
const NLP_API_URL = import.meta.env.VITE_NLP_API_URL || `${API_BASE_URL}/nlp/`;
const GENERATE_API_URL = import.meta.env.VITE_GENERATE_API_URL || `${API_BASE_URL}/generate/`;
const MEDIA_URL = import.meta.env.VITE_MEDIA_URL || 'http://localhost:8000/media/';
const CHAT_API_URL = import.meta.env.VITE_CHAT_API_URL || `${API_BASE_URL}/chat/`;

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true,
  timeout: 30000, // 30 second timeout to prevent hanging requests
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

// Add response interceptor for common error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle connection errors
    if (!error.response) {
      console.error('Network or connection error:', error.message);
      return Promise.reject(new Error('Could not connect to the server. Please check your network connection.'));
    }
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
    let retries = 2; // Number of retry attempts
    let lastError = null;
    
    while (retries >= 0) {
      try {
        console.log(`Uploading document via Axios (attempts remaining: ${retries})`);
        
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
          // Add timeout to prevent hanging request
          timeout: 30000,
        });
        
        console.log('Upload response:', response.data);
        return response.data;
      } catch (error) {
        lastError = error;
        console.error(`Error uploading document (attempts remaining: ${retries}):`, error);
        
        // If it's a network error (no response), wait and retry
        if (axios.isAxiosError(error) && !error.response) {
          console.log('Connection error detected, retrying after delay...');
          // Wait for 1 second before retrying
          await new Promise(resolve => setTimeout(resolve, 1000));
          retries--;
        } else {
          // For other types of errors, don't retry
          break;
        }
      }
    }
    
    // If we reached here, all retries failed
    throw lastError || new Error('Failed to upload document after multiple attempts');
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

  checkDocument: async (id: string) => {
    try {
      console.log(`Checking document ${id} status`);
      // First, get the document details
      const document = await apiClient.get(`${DOCUMENTS_API_URL}${id}/`);
      
      // Check if the file exists and is accessible
      try {
        const fileExists = await fetch(document.data.file, { method: 'HEAD' });
        if (!fileExists.ok) {
          console.warn(`Document file not accessible: ${document.data.file}`);
          return {
            status: 'warning',
            message: 'Document file exists but may not be accessible',
            document: document.data
          };
        }
      } catch (fileError) {
        console.error('Error checking file existence:', fileError);
      }
      
      // Check processing status
      if (document.data.processing_status === 'failed') {
        return {
          status: 'error',
          message: document.data.error_message || 'Document processing failed',
          document: document.data
        };
      }
      
      if (document.data.processing_status === 'pending' || document.data.processing_status === 'processing') {
        return {
          status: 'pending',
          message: 'Document is still being processed',
          document: document.data
        };
      }
      
      return {
        status: 'success',
        message: 'Document is ready',
        document: document.data
      };
    } catch (error) {
      console.error(`Error checking document ${id}:`, error);
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
  analyzeQuery: async (data: { query_text: string; document_ids?: string[]; operation_type?: string }) => {
    try {
      console.log('Sending analysis request:', data);
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, data);
      return response.data;
    } catch (error) {
      console.error('Error analyzing query:', error);
      // Check if it's a server error (500)
      if (axios.isAxiosError(error) && error.response?.status === 500) {
        console.error('Server error details:', error.response.data);
        throw new Error('Server encountered an error processing your request. Please try again later.');
      }
      throw error;
    }
  },

  getDocumentAnalysis: async (documentId: string) => {
    try {
      console.log(`Fetching analysis for document: ${documentId}`);
      
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, {
        document_id: documentId,
        action: 'get_analysis',
        request_type: 'get_analysis',
        is_frontend_request: true
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching document analysis:', error);
      
      if (error.response) {
        // Server responded with non-200 status
        if (error.response.status === 404) {
          console.log('No analysis found for document - needs to be triggered');
          throw { ...error, status: 404, message: 'Analysis not found' };
        } else if (error.response.status === 409) {
          console.log('Analysis already exists for document');
          // This is not actually an error, just return that it exists
          throw { status: 409, message: 'Analysis already exists' };
        } else if (error.response.status === 500) {
          console.error('Server error when fetching analysis:', error.response.data);
          throw { status: 500, message: 'Server error when fetching analysis' };
        }
      }
      
      throw error;
    }
  },

  triggerDocumentAnalysis: async (documentId: string) => {
    try {
      console.log(`Triggering analysis for document: ${documentId}`);
      
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, {
        document_id: documentId,
        action: 'analyze_document',
        request_type: 'analyze',
        is_frontend_request: true
      });
      
      return response.data;
    } catch (error: any) {
      console.error('Error triggering document analysis:', error);
      
      if (error.response) {
        // Check for specific error types
        if (error.response.status === 409) {
          console.log('Analysis already exists for document');
          // Return a structured message to allow the calling code to handle gracefully
          throw { status: 409, message: 'Analysis already exists' };
        } else if (error.response.status === 500) {
          console.error('Server error when triggering analysis:', error.response.data);
          throw { status: 500, message: 'Server error when triggering document analysis' };
        }
      }
      
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
      console.log(`Sending message for document: ${documentId}`);
      
      // Determine operation type from message content
      let operationType = 'chat';
      
      if (message.toLowerCase().includes('summarize')) {
        operationType = 'summarize';
      } else if (message.toLowerCase().includes('simplify')) {
        operationType = 'simplify';
      } else if (message.toLowerCase().includes('extract')) {
        operationType = 'extract_items';
      } else if (message.toLowerCase().includes('format') || message.toLowerCase().includes('structure')) {
        operationType = 'format';
      } else if (message.toLowerCase().includes('legal')) {
        operationType = 'legal_analysis';
      } else if (message.toLowerCase().includes('translate')) {
        operationType = 'translate';
      } else if (message.toLowerCase().includes('retry analysis') || message.toLowerCase().includes('analyze again')) {
        operationType = 'retry_analysis';
      }
      
      const response = await apiClient.post(`${CHAT_API_URL}messages/`, {
        document_id: documentId,
        content: message,
        operation_type: operationType,
        action: 'chat',
        is_frontend_request: true
      });
      
      // Format and return message objects
      if (response.data && response.data.conversation) {
        const messages = [];
        
        // Add user message
        if (response.data.conversation.user_message) {
          messages.push({
            id: response.data.conversation.user_message.id || `user-${Date.now()}`,
            role: 'user',
            content: response.data.conversation.user_message.content || message,
            created_at: response.data.conversation.user_message.created_at || new Date().toISOString()
          });
        } else {
          // Fallback if user message not returned
          messages.push({
            id: `user-${Date.now()}`,
            role: 'user',
            content: message,
            created_at: new Date().toISOString()
          });
        }
        
        // Add system response
        if (response.data.conversation.system_response) {
          messages.push({
            id: response.data.conversation.system_response.id || `system-${Date.now()}`,
            role: 'system',
            content: response.data.conversation.system_response.content || 'I processed your request.',
            created_at: response.data.conversation.system_response.created_at || new Date().toISOString()
          });
        } else {
          // Fallback if system response not returned
          messages.push({
            id: `system-${Date.now()}`,
            role: 'system',
            content: 'I processed your request but encountered an issue with the response format.',
            created_at: new Date().toISOString()
          });
        }
        
        return messages;
      } else {
        // Handle unexpected response format
        console.warn('Unexpected response format from chat API:', response.data);
        return [
          {
            id: `user-${Date.now()}`,
            role: 'user',
            content: message,
            created_at: new Date().toISOString()
          },
          {
            id: `system-${Date.now()}`,
            role: 'system',
            content: 'I received your message but encountered an issue processing it.',
            created_at: new Date().toISOString()
          }
        ];
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      
      if (error.response && error.response.status === 500) {
        console.error('Server error details:', error.response.data);
        throw new Error('The server encountered an error processing your message. Please try again later.');
      }
      
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
