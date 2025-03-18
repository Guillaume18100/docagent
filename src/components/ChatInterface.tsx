import React, { useState } from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { FileTextIcon, FileIcon, AlertCircleIcon, SendIcon, UserIcon, BotIcon } from 'lucide-react';

// Define document options with associated prompts
const documentOptions = [
  {
    id: 'summarize',
    label: 'Summarize the document',
    prompt: 'Please provide a concise summary of this document highlighting the key points.',
    icon: FileTextIcon
  },
  {
    id: 'simplify',
    label: 'Simplify the language',
    prompt: 'Please rewrite this document with simpler language while maintaining its meaning.',
    icon: FileTextIcon
  },
  {
    id: 'extract-action-items',
    label: 'Extract action items',
    prompt: 'Please extract all action items, tasks, and next steps from this document.',
    icon: FileTextIcon
  },
  {
    id: 'format-structure',
    label: 'Improve formatting and structure',
    prompt: 'Please suggest a better format and structure for this document to improve readability.',
    icon: FileTextIcon
  },
  {
    id: 'legal-analysis',
    label: 'Legal analysis',
    prompt: 'Please provide a legal analysis of this document, highlighting potential issues or concerns.',
    icon: FileTextIcon
  },
  {
    id: 'translate',
    label: 'Translate document',
    prompt: 'Please translate this document to French while maintaining its meaning and context.',
    icon: FileTextIcon
  }
];

const ChatInterface: React.FC = () => {
  const { currentDocument, chatMessages, isLoading, sendChatMessage } = useDocumentContext();
  const [selectedOption, setSelectedOption] = useState<string | null>(null);
  const [processingOption, setProcessingOption] = useState<boolean>(false);

  const handleOptionSelect = async (optionId: string) => {
    if (isLoading || processingOption) return;
    
    const option = documentOptions.find(opt => opt.id === optionId);
    if (!option) return;
    
    setSelectedOption(optionId);
    setProcessingOption(true);
    
    try {
      await sendChatMessage(option.prompt);
    } catch (error) {
      console.error('Error sending option prompt:', error);
    } finally {
      setProcessingOption(false);
    }
  };

  return (
    <div className="flex flex-col h-full rounded-2xl border bg-card animate-fade-in shadow-sm overflow-hidden">
      <div className="border-b bg-muted/20 p-4">
        <h2 className="text-lg font-medium">Document Assistant</h2>
        <p className="text-sm text-muted-foreground">
          Select an option to process your document
        </p>
      </div>
      
      <div className="flex-1 flex flex-col">
        <ScrollArea className="flex-1 p-4">
          {chatMessages.length > 0 ? (
            <div className="space-y-4 mb-4">
              {chatMessages.map((message, index) => (
                <div 
                  key={index} 
                  className={`flex items-start gap-3 ${
                    message.sender === 'user' ? 'justify-end' : 'justify-start'
                  }`}
                >
                  {message.sender === 'system' && (
                    <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
                      <BotIcon className="h-4 w-4" />
                    </div>
                  )}
                  <div 
                    className={`rounded-lg px-3 py-2 max-w-[80%] ${
                      message.sender === 'user' 
                        ? 'bg-primary text-primary-foreground' 
                        : 'bg-muted'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                  </div>
                  {message.sender === 'user' && (
                    <div className="flex h-8 w-8 shrink-0 select-none items-center justify-center rounded-md border bg-background shadow">
                      <UserIcon className="h-4 w-4" />
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : !currentDocument ? (
            <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
              <div className="bg-muted p-3 rounded-full">
                <FileIcon className="h-6 w-6 text-muted-foreground" />
              </div>
              <div>
                <h3 className="font-medium">No document uploaded</h3>
                <p className="text-sm text-muted-foreground">
                  Upload a document to start processing
                </p>
              </div>
            </div>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
              <div className="bg-blue-100 p-3 rounded-full">
                <FileTextIcon className="h-6 w-6 text-blue-500" />
              </div>
              <div className="space-y-1">
                <h3 className="font-medium">Document ready for processing</h3>
                <p className="text-sm text-muted-foreground">
                  Select an option below to process your document
                </p>
              </div>
            </div>
          )}
        </ScrollArea>
        
        <div className="p-4 border-t bg-background">
          {currentDocument ? (
            <div className="space-y-3">
              <div className="text-sm font-medium">Available operations:</div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {documentOptions.map((option) => (
                  <Button
                    key={option.id}
                    variant={selectedOption === option.id ? "default" : "outline"}
                    className="justify-start h-auto py-2"
                    onClick={() => handleOptionSelect(option.id)}
                    disabled={isLoading || processingOption}
                  >
                    <option.icon className="h-4 w-4 mr-2" />
                    <span>{option.label}</span>
                  </Button>
                ))}
              </div>
              {isLoading && (
                <div className="flex items-center space-x-2">
                  <Skeleton className="h-4 w-4 rounded-full animate-pulse" />
                  <span className="text-sm text-muted-foreground">Processing...</span>
                </div>
              )}
            </div>
          ) : (
            <Alert variant="default" className="bg-muted/50">
              <AlertCircleIcon className="h-4 w-4" />
              <AlertTitle>Upload a document</AlertTitle>
              <AlertDescription>
                Please upload a document to start using the document assistant.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
