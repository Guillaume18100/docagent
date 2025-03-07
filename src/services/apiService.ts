
import axios from 'axios';

// Base API configuration
const apiClient = axios.create({
  baseURL: 'http://localhost:8000/api', // Replace with your actual backend API URL
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds timeout
});

// File upload specific client with multipart/form-data header
const fileUploadClient = axios.create({
  baseURL: 'http://localhost:8000/api',
  headers: {
    'Content-Type': 'multipart/form-data',
  },
  timeout: 60000, // 60 seconds timeout for file uploads
});

/**
 * Document API service
 */
export const documentService = {
  /**
   * Upload a document to the server
   * @param file - The file to upload
   * @returns Promise with the upload result
   */
  uploadDocument: async (file: File) => {
    const formData = new FormData();
    formData.append('document', file);
    
    try {
      const response = await fileUploadClient.post('/documents/upload/', formData);
      return response.data;
    } catch (error) {
      console.error('Error uploading document:', error);
      throw error;
    }
  },

  /**
   * Get document preview/draft
   * @param documentId - ID of the document to preview
   * @returns Promise with the document data
   */
  getDocumentPreview: async (documentId: string) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}/preview/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching document preview:', error);
      throw error;
    }
  },

  /**
   * Download the finished document
   * @param documentId - ID of the document to download
   * @returns Promise with the document blob
   */
  downloadDocument: async (documentId: string) => {
    try {
      const response = await apiClient.get(`/documents/${documentId}/download/`, {
        responseType: 'blob',
      });
      return response.data;
    } catch (error) {
      console.error('Error downloading document:', error);
      throw error;
    }
  }
};

/**
 * Chat API service
 */
export const chatService = {
  /**
   * Send a message to the chat
   * @param documentId - ID of the document this message is related to
   * @param message - The message text
   * @returns Promise with the chat response
   */
  sendMessage: async (documentId: string, message: string) => {
    try {
      const response = await apiClient.post('/chat/message/', {
        document_id: documentId,
        message,
      });
      return response.data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  },

  /**
   * Get chat history for a document
   * @param documentId - ID of the document
   * @returns Promise with the chat history
   */
  getChatHistory: async (documentId: string) => {
    try {
      const response = await apiClient.get(`/chat/history/${documentId}/`);
      return response.data;
    } catch (error) {
      console.error('Error fetching chat history:', error);
      throw error;
    }
  }
};
