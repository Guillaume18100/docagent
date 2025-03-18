import React, { createContext, useState, useContext, useCallback, ReactNode } from 'react';
import { useToast } from "@/components/ui/use-toast";
import { documentService, chatService, nlpApi } from '@/services/apiService';
import { Document, ChatMessage, DocumentPreview, DocumentAnalysis, DocumentContextType } from '@/types';

// Create the context with default values
const DocumentContext = createContext<DocumentContextType>({
  currentDocument: null,
  documentPreview: null,
  documentAnalysis: null,
  chatMessages: [],
  isLoading: false,
  setCurrentDocument: () => {},
  refreshDocumentPreview: async () => {},
  refreshDocumentAnalysis: async () => {},
  sendChatMessage: async () => {},
});

export const useDocumentContext = () => useContext(DocumentContext);

interface DocumentProviderProps {
  children: ReactNode;
}

export const DocumentProvider: React.FC<DocumentProviderProps> = ({ children }) => {
  const [currentDocument, setCurrentDocument] = useState<Document | null>(null);
  const [documentPreview, setDocumentPreview] = useState<DocumentPreview | null>(null);
  const [documentAnalysis, setDocumentAnalysis] = useState<DocumentAnalysis | null>(null);
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
      console.error("Preview error:", error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast]);

  // Refresh document analysis
  const refreshDocumentAnalysis = useCallback(async () => {
    if (!currentDocument) return;
    
    setIsLoading(true);
    let retryCount = 0;
    const maxRetries = 2;
    
    // First, verify the document is properly processed
    try {
      const checkResult = await documentService.checkDocument(currentDocument.id);
      console.log('Document check result:', checkResult);
      
      if (checkResult.status === 'error') {
        toast({
          title: "Document Error",
          description: checkResult.message || "The document has processing errors",
          variant: "destructive",
        });
        setIsLoading(false);
        return;
      }
      
      if (checkResult.status === 'pending') {
        toast({
          title: "Document Processing",
          description: "The document is still being processed. Try again in a moment.",
        });
        setIsLoading(false);
        return;
      }
    } catch (error) {
      console.error('Error checking document:', error);
      // Continue even if check fails
    }
    
    const attemptAnalysis = async () => {
      try {
        console.log("Attempting to get existing analysis for document:", currentDocument.id);
        // First try to get existing analysis
        let analysis = await nlpApi.getDocumentAnalysis(currentDocument.id);
        
        // If no analysis exists, trigger a new one
        if (!analysis) {
          console.log("No existing analysis found, triggering new analysis");
          analysis = await nlpApi.triggerDocumentAnalysis(currentDocument.id);
        }
        
        console.log("Received analysis:", analysis);
        if (analysis) {
          setDocumentAnalysis(analysis);
          return true;
        } else {
          throw new Error("Empty analysis response");
        }
      } catch (error) {
        console.error("Analysis error:", error);
        if (retryCount < maxRetries) {
          console.log(`Retrying analysis (${retryCount + 1}/${maxRetries})...`);
          retryCount++;
          // Wait 1 second before retrying
          await new Promise(resolve => setTimeout(resolve, 1000));
          return await attemptAnalysis();
        }
        
        // Create a placeholder analysis with error status if all retries fail
        setDocumentAnalysis({
          id: 'error',
          document: currentDocument.id,
          summary: '',
          keywords: [],
          sentiment: '',
          entities: {},
          topics: [],
          status: 'failed',
          error_message: 'Failed to load document analysis after multiple attempts',
          created_at: new Date().toISOString()
        });
        
        toast({
          title: "Analysis Error",
          description: "Unable to analyze document. The server might be experiencing issues. Try again later.",
          variant: "destructive",
        });
        return false;
      }
    };
    
    await attemptAnalysis();
    setIsLoading(false);
  }, [currentDocument, toast]);

  // Add this right after the refreshDocumentAnalysis function
  const createFallbackAnalysis = useCallback(() => {
    if (!currentDocument) return null;
    
    console.log('Creating fallback analysis for document:', currentDocument.id);
    
    // This creates a minimal analysis object that will allow the app to continue
    return {
      id: `fallback-${currentDocument.id}`,
      document: currentDocument.id,
      summary: 'Document analysis is currently unavailable. You can still chat about this document.',
      keywords: [],
      sentiment: 'neutral',
      entities: {},
      topics: ['general'],
      status: 'limited',
      error_message: '',
      created_at: new Date().toISOString()
    };
  }, [currentDocument]);

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
      console.error("Chat history error:", error);
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast]);

  // Update the sendChatMessage function to work even without analysis
  const sendChatMessage = useCallback(async (message: string) => {
    if (!currentDocument) return;
    
    setIsLoading(true);
    // Create a temporary ID that we can reliably remove if needed
    const tempId = `temp-${Date.now()}`;
    
    // Define tempUserMessage outside the try block so it's available everywhere
    const tempUserMessage: ChatMessage = {
      id: tempId,
      document_id: currentDocument.id,
      content: message,
      sender: 'user',
      timestamp: new Date().toISOString(),
    };
    
    try {
      // Optimistically add the user message
      setChatMessages(prev => [...prev, tempUserMessage]);
      
      // Check if this is a request to retry analysis
      if (message.toLowerCase().includes('retry analysis') || 
          message.toLowerCase().includes('analyze again')) {
        
        // Replace temp message with confirmed user message
        setChatMessages(prev => {
          const filtered = prev.filter(msg => msg.id !== tempId);
          return [...filtered, {
            ...tempUserMessage,
            id: `user-${Date.now()}`
          }];
        });
        
        // Add system message that we're retrying analysis
        const systemMessage: ChatMessage = {
          id: `system-${Date.now()}`,
          document_id: currentDocument.id,
          content: "I'll retry analyzing this document for you.",
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        };
        setChatMessages(prev => [...prev, systemMessage]);
        
        // Trigger analysis refresh
        await refreshDocumentAnalysis();
        
        // Add a confirmation message after analysis completes
        const completionMessage: ChatMessage = {
          id: `system-${Date.now() + 1}`,
          document_id: currentDocument.id,
          content: documentAnalysis?.status === 'failed' 
            ? "I tried to analyze the document again, but there are still some issues. You can continue chatting though." 
            : "I've completed the document analysis. You can now ask me questions about it.",
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        };
        setChatMessages(prev => [...prev, completionMessage]);
        setIsLoading(false);
        return;
      }
      
      // If we don't have an analysis and this isn't a retry attempt,
      // create a fallback analysis if needed
      if (!documentAnalysis) {
        const fallback = createFallbackAnalysis();
        if (fallback) {
          setDocumentAnalysis(fallback);
        }
      }
      
      // Send to API
      console.log(`Sending message for document ${currentDocument.id}:`, message);
      let response;
      let retryCount = 0;
      const maxRetries = 2;
      
      const sendWithRetry = async () => {
        try {
          return await chatService.sendMessage(currentDocument.id, message);
        } catch (error) {
          console.error(`Send message error (attempt ${retryCount + 1}):`, error);
          if (retryCount < maxRetries) {
            retryCount++;
            // Wait before retrying
            await new Promise(resolve => setTimeout(resolve, 1000));
            return await sendWithRetry();
          }
          throw error;
        }
      };
      
      response = await sendWithRetry();
      console.log("Message response:", response);
      
      // Replace temp message with real message and add system response
      if (response && response.userMessage && response.systemResponse) {
        setChatMessages(prev => {
          const filtered = prev.filter(msg => msg.id !== tempId);
          return [...filtered, response.userMessage, response.systemResponse];
        });
      } else {
        // If we don't get a proper response, add a generic system response
        const genericResponse: ChatMessage = {
          id: `system-${Date.now()}`,
          document_id: currentDocument.id,
          content: "I processed your request, but couldn't generate a specific response. Please try again with a different query.",
          sender: 'assistant',
          timestamp: new Date().toISOString(),
        };
        
        setChatMessages(prev => {
          // Replace temp message with confirmed one
          const filtered = prev.filter(msg => msg.id !== tempId);
          return [...filtered, 
            {...tempUserMessage, id: `user-${Date.now()}`},
            genericResponse
          ];
        });
      }
      
      // Refresh the document preview after sending a message
      await refreshDocumentPreview();
      
    } catch (error) {
      console.error("Send message error:", error);
      
      // Remove the temp message on error
      setChatMessages(prev => prev.filter(msg => msg.id !== tempId));
      
      // Add a system error message instead
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        document_id: currentDocument.id,
        content: "Sorry, I encountered an error processing your request. The server might be busy or experiencing issues. You can try again or ask something simpler.",
        sender: 'assistant',
        timestamp: new Date().toISOString(),
      };
      
      // Add the user message with a confirmed ID and the error message
      setChatMessages(prev => [...prev, 
        {...tempUserMessage, id: `user-${Date.now()}`},
        errorMessage
      ]);
      
      toast({
        title: "Request Failed",
        description: "Couldn't process your request. You can continue chatting though.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [currentDocument, toast, refreshDocumentPreview, documentAnalysis, createFallbackAnalysis, refreshDocumentAnalysis]);

  // Update chat history, document preview, and analysis when current document changes
  React.useEffect(() => {
    if (currentDocument) {
      // Load chat history, but don't block on failure
      loadChatHistory().catch(err => {
        console.error("Error loading chat history:", err);
        setChatMessages([]); // Reset to empty on error
      });
      
      // Load document preview, but don't block on failure
      refreshDocumentPreview().catch(err => {
        console.error("Error loading document preview:", err);
        // Preview can be null, so we're already covered
      });
      
      // Try to get analysis, but don't block other functionality if it fails
      refreshDocumentAnalysis().catch(err => {
        console.error("Failed to load document analysis:", err);
        const fallback = createFallbackAnalysis();
        if (fallback) {
          setDocumentAnalysis(fallback);
        }
        toast({
          title: "Analysis Issue",
          description: "Document analysis couldn't be loaded. Basic chat functionality is still available.",
          variant: "warning",
        });
      });
    } else {
      setChatMessages([]);
      setDocumentPreview(null);
      setDocumentAnalysis(null);
    }
  }, [currentDocument, loadChatHistory, refreshDocumentPreview, refreshDocumentAnalysis, createFallbackAnalysis, toast]);

  const value = {
    currentDocument,
    documentPreview,
    documentAnalysis,
    chatMessages,
    isLoading,
    setCurrentDocument,
    refreshDocumentPreview,
    refreshDocumentAnalysis,
    sendChatMessage,
  };

  return (
    <DocumentContext.Provider value={value}>
      {children}
    </DocumentContext.Provider>
  );
};
