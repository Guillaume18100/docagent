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
      console.log(`Fetching analysis for document ID: ${documentId}`);
      // CRITICAL FIX: Force using the analyze_document action via POST to avoid the missing get_document_analysis method
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, {
        document_id: documentId,
        action: 'analyze_document', // Changed from 'get_analysis' to 'analyze_document'
        request_type: 'get_existing_analysis', // Clarify we want to get existing analysis
        is_frontend_request: true, // Add debugging flag
        method_hint: 'post_only' // Add hint that we're avoiding GET completely
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching analysis for document ${documentId}:`, error);
      
      if (axios.isAxiosError(error)) {
        if (error.response?.status === 404) {
          console.log('Analysis not found for document, will need to trigger a new one');
          return null; // Return null to indicate we need to create a new analysis
        } else if (error.response?.status === 500) {
          console.error('Server error details:', error.response.data);
          throw new Error('The server encountered an error retrieving document analysis.');
        }
      }
      throw error;
    }
  },

  triggerDocumentAnalysis: async (documentId: string) => {
    try {
      console.log(`Triggering analysis for document ID: ${documentId}`);
      // Focus on using the regular analyze endpoint with very explicit action
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, {
        document_id: documentId,
        action: 'analyze_document',
        method: 'analyze_document', // Add method parameter for clarity
        operation: 'create',  // Specify this is creating a new analysis
        request_type: 'analyze',
        is_frontend_request: true, // Add debugging flag
        method_hint: 'post_only' // Add hint that we're avoiding GET completely
      });
      return response.data;
    } catch (error) {
      console.error(`Error triggering analysis for document ${documentId}:`, error);
      
      if (axios.isAxiosError(error) && error.response?.status === 500) {
        console.error('Server error details:', error.response.data);
        throw new Error('Server error while analyzing document. Try again later.');
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
  
  sendMessage: async (documentId: number, message: string) => {
    try {
      console.log(`Sending message for document ${documentId}: ${message}`);
      
      // Extract operation type from the message if possible
      let operationType = 'general';
      const messageLower = message.toLowerCase();
      if (messageLower.includes('summarize')) operationType = 'summarize';
      if (messageLower.includes('simplify')) operationType = 'simplify';
      if (messageLower.includes('extract')) operationType = 'extract';
      if (messageLower.includes('format')) operationType = 'format';
      if (messageLower.includes('legal')) operationType = 'legal';
      if (messageLower.includes('translate')) operationType = 'translate';
      if (messageLower.includes('retry analysis') || messageLower.includes('analyze again')) {
        operationType = 'analyze';
      }
      
      console.log(`Detected operation type: ${operationType}`);
      
      // Map to the new API - create a new user query or add to conversation
      const payload = {
        document_id: documentId,
        query_text: message,
        operation_type: operationType,
        is_frontend_request: true, // Add debugging flag
        action: 'chat', // Clarify the intent
        request_type: 'chat' // Indicate the type of request consistently
      };
      
      console.log('Sending payload:', payload);
      
      const response = await apiClient.post(`${NLP_API_URL}analyze/`, payload);
      
      console.log('Response from server:', response.data);
      
      if (response.data && (response.data.conversation || response.data.result)) {
        // If we get a conversation object back with messages, extract them
        console.log('Received conversation response:', response.data);
        return {
          userMessage: {
            id: `user-${Date.now()}`,
            document_id: documentId,
            content: message,
            sender: 'user',
            timestamp: new Date().toISOString(),
          },
          systemResponse: {
            id: `system-${Date.now()}`,
            document_id: documentId,
            content: response.data.result || 
                     (response.data.messages && response.data.messages.length > 1 ? 
                      response.data.messages[1].content : 
                      "I've processed your request."),
            sender: 'assistant',
            timestamp: new Date().toISOString(),
          }
        };
      } else {
        // Default response structure
        console.log('Received generic response - creating default message structure');
        return {
          userMessage: {
            id: `user-${Date.now()}`,
            document_id: documentId,
            content: message,
            sender: 'user',
            timestamp: new Date().toISOString(),
          },
          systemResponse: {
            id: `system-${Date.now()}`,
            document_id: documentId,
            content: response.data?.message || 'I have processed your request.',
            sender: 'assistant',
            timestamp: new Date().toISOString(),
          }
        };
      }
    } catch (error) {
      console.error(`Error sending message for document ${documentId}:`, error);
      
      if (axios.isAxiosError(error) && error.response?.status === 500) {
        console.error('Server error details:', error.response?.data);
        throw new Error('Server error while processing your request. Try a simpler query or try again later.');
      }
      
      // Return a fallback message pair to avoid cascading errors
      return {
        userMessage: {
          id: `user-error-${Date.now()}`,
          document_id: documentId,
          content: message,
          sender: 'user',
          timestamp: new Date().toISOString(),
        },
        systemResponse: {
          id: `system-error-${Date.now()}`,
          document_id: documentId,
          content: "I'm sorry, I encountered an error processing your request. The server might be experiencing issues. Please try again later.",
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        }
      };
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
