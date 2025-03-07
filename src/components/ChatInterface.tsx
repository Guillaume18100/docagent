import React, { useState, useRef, useEffect } from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Badge } from "@/components/ui/badge";
import { SendIcon, RefreshCwIcon, FileIcon, InfoIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ChatMessage } from '@/types';
import { useToast } from "@/components/ui/use-toast";

const ChatInterface: React.FC = () => {
  const { chatMessages, sendChatMessage, isLoading, currentDocument } = useDocumentContext();
  const [message, setMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const [documentGenerated, setDocumentGenerated] = useState<boolean>(false);
  const { toast } = useToast();

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!message.trim() || !currentDocument) return;
    
    // Reset the document generated state
    setDocumentGenerated(false);
    
    try {
      const response = await sendChatMessage(message.trim());
      
      // Check if a document was generated based on the message
      if (response?.documentGenerated) {
        setDocumentGenerated(true);
        
        // Show a toast notification
        toast({
          title: "Document Generation Started",
          description: "Your document is being generated. Check the 'Generate Documents' tab when it's ready.",
          duration: 5000,
        });
      }
    } catch (error) {
      console.error("Error sending message:", error);
    }
    
    setMessage('');
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  // Format timestamp for display
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="flex flex-col h-full border rounded-lg overflow-hidden bg-card">
      <div className="px-4 py-3 border-b bg-muted/50 flex justify-between items-center">
        <h3 className="font-semibold text-lg">Document Chat</h3>
        
        {currentDocument && (
          <Badge variant="outline" className="flex items-center gap-1">
            <FileIcon className="h-3 w-3" />
            <span className="text-xs truncate max-w-[150px]">{currentDocument.name}</span>
          </Badge>
        )}
      </div>
      
      <ScrollArea className="flex-1 p-4" ref={scrollAreaRef}>
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4">
            <InfoIcon className="h-8 w-8 text-muted-foreground mb-2" />
            <h3 className="font-medium text-lg">Start Chatting</h3>
            <p className="text-sm text-muted-foreground max-w-xs">
              Ask questions about your document or request to generate new documents based on it.
            </p>
            
            <div className="mt-6 text-sm bg-muted/50 p-4 rounded-lg border text-left">
              <p className="font-medium mb-2">Example prompts you can try:</p>
              <ul className="space-y-2">
                <li>• "Summarize this document for me"</li>
                <li>• "What are the key points in this document?"</li>
                <li>• "Generate a similar document for [another topic]"</li>
                <li>• "Create a PDF version of this with more details about [topic]"</li>
              </ul>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {chatMessages.map((msg, index) => (
              <div
                key={msg.id}
                className={cn(
                  "flex w-max max-w-[85%] flex-col gap-2 rounded-lg px-3 py-2 text-sm",
                  msg.sender === 'user'
                    ? "ml-auto bg-primary text-primary-foreground"
                    : "bg-muted"
                )}
              >
                <div className="whitespace-pre-line break-words">
                  {msg.content}
                </div>
                <div 
                  className={cn(
                    "text-xs opacity-70 self-end",
                    msg.sender === 'user' ? "text-primary-foreground" : "text-muted-foreground"
                  )}
                >
                  {formatTime(msg.timestamp)}
                </div>
              </div>
            ))}
            
            {documentGenerated && (
              <Alert className="bg-blue-50 border-blue-200">
                <RefreshCwIcon className="h-4 w-4 text-blue-500 animate-spin" />
                <AlertTitle>Document Generation In Progress</AlertTitle>
                <AlertDescription>
                  Your document is being generated based on your request.
                  Check the "Generate Documents" tab to see when it's ready for download.
                </AlertDescription>
              </Alert>
            )}
            
            {isLoading && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground italic pl-2">
                <div className="flex gap-1">
                  <span className="animate-bounce">.</span>
                  <span className="animate-bounce animation-delay-200">.</span>
                  <span className="animate-bounce animation-delay-400">.</span>
                </div>
                <span>Thinking</span>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        )}
      </ScrollArea>
      
      <div className="p-4 border-t bg-background">
        <div className="flex items-end space-x-2">
          <Textarea
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Type your requirements or questions..."
            className="min-h-[80px] resize-none border-muted"
            disabled={isLoading || !currentDocument}
          />
          <Button
            onClick={handleSendMessage}
            disabled={!message.trim() || isLoading || !currentDocument}
            className="h-10 w-10 rounded-full p-0 flex-shrink-0"
          >
            <SendIcon className="h-5 w-5" />
          </Button>
        </div>
        {!currentDocument && (
          <p className="text-xs text-muted-foreground mt-2">
            Please upload a document first to start the conversation
          </p>
        )}
      </div>
    </div>
  );
};

export default ChatInterface;
