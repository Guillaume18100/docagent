import React, { createContext, useState, useContext, useCallback, ReactNode } from 'react';
import { useToast } from "@/components/ui/use-toast";
import { documentService, chatService } from '@/services/apiService';
import { Document, ChatMessage, DocumentPreview, DocumentContextType } from '@/types';

// Create the context with default values
const DocumentContext = createContext<DocumentContextType>({
  currentDocument: null,
  documentPreview: null,
  chatMessages: [],
  isLoading: false,
  setCurrentDocument: () => {},
  refreshDocumentPreview: async () => {},
  sendChatMessage: async () => {},
});

export const useDocumentContext = () => useContext(DocumentContext);

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [documentPreview, setDocumentPreview] = useState<DocumentPreview | null>(null);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const { toast } = useToast();

  // Refresh document preview
  const refreshDocumentPreview = useCallback(async () => {
    if (!currentDocument) return;
    
    setIsLoading(true);
    try {
      const preview = await documentService.getDocumentPreview(currentDocument.id);
      setDocumentPreview(preview);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load document preview",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast]);

  // Load chat history when document changes
  const loadChatHistory = useCallback(async () => {
    if (!currentDocument) return;
    
    setIsLoading(true);
    try {
      const history = await chatService.getChatHistory(currentDocument.id);
      setChatMessages(history);
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to load chat history",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast]);

  // Send a chat message
  const sendChatMessage = useCallback(async (message: string) => {
    if (!currentDocument) return;
    
    setIsLoading(true);
    try {
      // Optimistically add the user message
      const tempUserMessage: ChatMessage = {
        id: `temp-${Date.now()}`,
        document_id: currentDocument.id,
        content: message,
        sender: 'user',
        timestamp: new Date().toISOString(),
      };
      
      setChatMessages(prev => [...prev, tempUserMessage]);
      
      // Send to API
      const response = await chatService.sendMessage(currentDocument.id, message);
      
      // Replace temp message with real message and add system response
      setChatMessages(prev => {
        const filtered = prev.filter(msg => msg.id !== tempUserMessage.id);
        return [...filtered, response.userMessage, response.systemResponse];
      });
      
      // Refresh the document preview after sending a message
      await refreshDocumentPreview();
      
      // Return the full response so components can see if a document was generated
      return response;
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast, refreshDocumentPreview]);

  // Update chat history and document preview when current document changes
  React.useEffect(() => {
    if (currentDocument) {
      loadChatHistory();
      refreshDocumentPreview();
    } else {
      setChatMessages([]);
      setDocumentPreview(null);
    }
  }, [currentDocument, loadChatHistory, refreshDocumentPreview]);

  const value = {
    currentDocument,
    documentPreview,
    chatMessages,
    isLoading,
    setCurrentDocument,
    refreshDocumentPreview,
    sendChatMessage,
  };

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};
