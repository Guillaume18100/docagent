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
    
    try {
      console.log("Refreshing document analysis for:", currentDocument.id);
      
      // Check if document is processed in the backend
      const documentCheck = await documentService.checkDocument(currentDocument.id);
      console.log("Document check result:", documentCheck);
      
      // If the document has an error status
      if (documentCheck.status === 'error') {
        toast({
          title: "Error processing document",
          description: documentCheck.message || "There was an error processing your document.",
          variant: "destructive"
        });
        setIsLoading(false);
        return;
      }
      
      // If document is still being processed
      if (documentCheck.status === 'pending') {
        toast({
          title: "Document is still processing",
          description: "Your document is still being processed. Please try again shortly.",
          variant: "default"
        });
        setIsLoading(false);
        return;
      }
      
      // Try to get existing analysis
      let maxRetries = 2;
      let retryCount = 0;
      let success = false;
      
      // Create a function to attempt getting or creating the analysis
      const attemptAnalysis = async () => {
        try {
          // First try to get any existing analysis
          const analysis = await nlpApi.getDocumentAnalysis(currentDocument.id);
          console.log("Existing analysis found:", analysis);
          setDocumentAnalysis(analysis);
          success = true;
        } catch (error: any) {
          console.log("Error fetching analysis:", error);
          
          // If the error message indicates analysis already exists, we can consider this a success
          if (error.message && error.message.includes("Analysis already exists")) {
            console.log("Analysis already exists, trying to get existing analysis");
            try {
              // Fetch the existing analysis
              const analysis = await nlpApi.getDocumentAnalysis(currentDocument.id);
              setDocumentAnalysis(analysis);
              success = true;
              return;
            } catch (secondError) {
              console.error("Failed to get existing analysis:", secondError);
            }
          }
          
          // If analysis doesn't exist, try to trigger a new one
          if (error.status === 404) {
            try {
              console.log("No analysis found, triggering new analysis");
              const newAnalysis = await nlpApi.triggerDocumentAnalysis(currentDocument.id);
              setDocumentAnalysis(newAnalysis);
              success = true;
            } catch (triggerError: any) {
              if (triggerError.message && triggerError.message.includes("Analysis already exists")) {
                console.log("Analysis creation reports it already exists - attempting to fetch existing");
                try {
                  // One final attempt to fetch existing analysis
                  const existingAnalysis = await nlpApi.getDocumentAnalysis(currentDocument.id);
                  setDocumentAnalysis(existingAnalysis);
                  success = true;
                  return;
                } catch (finalError) {
                  console.error("Final attempt to get analysis failed:", finalError);
                  throw finalError;
                }
              } else {
                console.error("Error triggering analysis:", triggerError);
                throw triggerError;
              }
            }
          } else {
            throw error;
          }
        }
      };
      
      // Attempt with retries
      while (retryCount < maxRetries && !success) {
        try {
          await attemptAnalysis();
        } catch (error: any) {
          retryCount++;
          console.log(`Attempt ${retryCount} failed, ${maxRetries - retryCount} retries left`);
          if (retryCount < maxRetries) {
            // Wait 1 second before retry
            await new Promise(resolve => setTimeout(resolve, 1000));
          } else {
            // Create a placeholder analysis with error status if all retries fail
            console.error("All analysis attempts failed:", error);
            const errorMessage = error.message || "Failed to analyze document";
            
            // If createFallbackAnalysis is defined, use it to create a fallback
            if (typeof createFallbackAnalysis === 'function') {
              const fallbackAnalysis = createFallbackAnalysis();
              if (fallbackAnalysis) {
                fallbackAnalysis.status = 'error';
                fallbackAnalysis.error_message = errorMessage;
                setDocumentAnalysis(fallbackAnalysis);
              }
            }
            
            toast({
              title: "Analysis failed",
              description: errorMessage,
              variant: "destructive"
            });
          }
        }
      }
    } catch (error: any) {
      console.error("Error in document analysis process:", error);
      toast({
        title: "Error",
        description: error.message || "An error occurred while analyzing the document.",
        variant: "destructive"
      });
    } finally {
      setIsLoading(false);
    }
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

  // Update the sendChatMessage function to work with the new message format being returned from the API service.
  const sendChatMessage = async (messageContent: string) => {
    if (!currentDocument) return;
    
    const tempId = `user-${Date.now()}`;
    
    // Create temp user message for optimistic UI update
    setChatMessages(prev => [
      ...prev, 
      {
        id: tempId,
        role: 'user',
        content: messageContent,
        created_at: new Date().toISOString()
      }
    ]);
    
    setIsLoading(true);
    
    try {
      // Check if we need to retry document analysis
      if (
        messageContent.toLowerCase().includes('retry analysis') || 
        messageContent.toLowerCase().includes('analyze again')
      ) {
        setChatMessages(prev => [
          ...prev, 
          {
            id: `system-${Date.now()}`,
            role: 'system',
            content: 'Retrying document analysis...',
            created_at: new Date().toISOString()
          }
        ]);
        
        await refreshDocumentAnalysis();
        
        // Add confirmation message after analysis completes
        const statusMessage = documentAnalysis && documentAnalysis.status === 'completed'
          ? 'Analysis completed successfully! You can now continue with your requests.'
          : 'Analysis process completed, but there may still be issues. Please check the analysis tab.';
          
        setChatMessages(prev => [
          ...prev, 
          {
            id: `system-${Date.now() + 1}`,
            role: 'system',
            content: statusMessage,
            created_at: new Date().toISOString()
          }
        ]);
        
        setIsLoading(false);
        return;
      }
      
      // If no analysis exists and we're not asking to retry, create fallback
      if (!documentAnalysis && !messageContent.toLowerCase().includes('retry analysis')) {
        if (typeof createFallbackAnalysis === 'function') {
          const fallback = createFallbackAnalysis();
          if (fallback) {
            console.log("Setting fallback analysis for chat:", fallback);
            setDocumentAnalysis(fallback);
          }
        }
      }
      
      // Try to send message with retries
      let maxRetries = 2;
      let retryCount = 0;
      let success = false;
      let responseMessages = null;
      
      while (retryCount <= maxRetries && !success) {
        try {
          responseMessages = await nlpApi.sendMessage(currentDocument.id, messageContent);
          success = true;
        } catch (error) {
          console.error(`Message send error (attempt ${retryCount + 1}/${maxRetries + 1}):`, error);
          retryCount++;
          
          if (retryCount <= maxRetries) {
            // Wait 1 second before retry
            await new Promise(resolve => setTimeout(resolve, 1000));
          } else {
            // Add error message if all retries fail
            setChatMessages(prev => {
              // Filter out the temp message we added
              const filtered = prev.filter(msg => msg.id !== tempId);
              
              // Add both the actual user message and error response
              return [
                ...filtered,
                {
                  id: `user-${Date.now()}`,
                  role: 'user',
                  content: messageContent,
                  created_at: new Date().toISOString()
                },
                {
                  id: `system-${Date.now()}`,
                  role: 'system',
                  content: "I'm sorry, I encountered an error processing your message. Please try again later.",
                  created_at: new Date().toISOString()
                }
              ];
            });
            
            setIsLoading(false);
            throw error;
          }
        }
      }
      
      if (success && responseMessages) {
        setChatMessages(prev => {
          // Filter out the temp message we added
          const filtered = prev.filter(msg => msg.id !== tempId);
          
          // Add the confirmed messages from the API
          return [...filtered, ...responseMessages];
        });
        
        // Refresh document preview after sending a message
        refreshDocumentPreview();
      }
    } catch (error) {
      console.error('Error in sendChatMessage:', error);
    } finally {
      setIsLoading(false);
    }
  };

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
