
import React, { useState, useRef, useEffect } from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { SendIcon, RefreshCwIcon } from 'lucide-react';
import { cn } from '@/lib/utils';
import { ChatMessage } from '@/types';

const ChatInterface: React.FC = () => {
  const { chatMessages, sendChatMessage, isLoading, currentDocument } = useDocumentContext();
  const [message, setMessage] = useState<string>('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  const handleSendMessage = async () => {
    if (!message.trim() || !currentDocument) return;
    
    await sendChatMessage(message.trim());
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
    <div className="flex flex-col h-full rounded-2xl border bg-card animate-fade-in shadow-sm overflow-hidden">
      <div className="p-4 border-b bg-muted/20">
        <h2 className="text-lg font-medium">Document Requirements</h2>
        <p className="text-sm text-muted-foreground">
          Specify your requirements or ask questions about the document
        </p>
      </div>
      
      <ScrollArea 
        className="flex-1 p-4" 
        ref={scrollAreaRef}
        type="always"
      >
        {chatMessages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-primary/10 p-3 rounded-full">
              <RefreshCwIcon className="h-5 w-5 text-primary" />
            </div>
            <div>
              <h3 className="font-medium">No messages yet</h3>
              <p className="text-sm text-muted-foreground">
                Start by describing your document requirements or asking a question
              </p>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            {chatMessages.map((msg: ChatMessage) => (
              <div 
                key={msg.id}
                className={cn(
                  "flex flex-col max-w-[80%] space-y-1",
                  msg.sender === "user" 
                    ? "ml-auto items-end" 
                    : "mr-auto items-start"
                )}
              >
                <div
                  className={cn(
                    "p-3 rounded-xl animate-scale-in",
                    msg.sender === "user"
                      ? "bg-primary text-primary-foreground rounded-tr-none"
                      : "bg-muted rounded-tl-none"
                  )}
                >
                  <p className="text-sm whitespace-pre-wrap break-words">
                    {msg.content}
                  </p>
                </div>
                <span className="text-xs text-muted-foreground">
                  {formatTime(msg.timestamp)}
                </span>
              </div>
            ))}
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
