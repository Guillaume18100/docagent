import React, { useState } from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { ScrollArea } from "@/components/ui/scroll-area";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Progress } from "@/components/ui/progress";
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from "@/components/ui/collapsible";
import { Badge } from "@/components/ui/badge";
import { 
  FileTextIcon, 
  FileIcon, 
  AlertCircleIcon, 
  CheckIcon, 
  ChevronDownIcon, 
  RefreshCwIcon,
  ArrowDownIcon,
  ScanIcon,
  LucideIcon,
  ListChecksIcon,
  BookOpenIcon,
  FilePenIcon,
  ScaleIcon,
  LanguagesIcon,
  ArrowRightIcon,
  MinusCircleIcon
} from 'lucide-react';

// Define document actions with descriptions and icons
const documentActions = [
  {
    id: 'summarize',
    label: 'Summarize Document',
    description: 'Create a concise summary of the document highlighting key points',
    prompt: 'Please provide a concise summary of this document highlighting the key points.',
    icon: BookOpenIcon,
    resultTitle: 'Document Summary'
  },
  {
    id: 'simplify',
    label: 'Simplify Language',
    description: 'Rewrite the document using simpler language while maintaining meaning',
    prompt: 'Please rewrite this document with simpler language while maintaining its meaning.',
    icon: FilePenIcon,
    resultTitle: 'Simplified Content'
  },
  {
    id: 'extract-action-items',
    label: 'Extract Action Items',
    description: 'Identify and list all tasks, action items, and next steps from the document',
    prompt: 'Please extract all action items, tasks, and next steps from this document.',
    icon: ListChecksIcon,
    resultTitle: 'Action Items'
  },
  {
    id: 'format-structure',
    label: 'Improve Structure',
    description: 'Suggest better formatting and structure to enhance readability',
    prompt: 'Please suggest a better format and structure for this document to improve readability.',
    icon: ScanIcon,
    resultTitle: 'Improved Structure'
  },
  {
    id: 'legal-analysis',
    label: 'Legal Analysis',
    description: 'Analyze legal aspects and highlight potential issues or concerns',
    prompt: 'Please provide a legal analysis of this document, highlighting potential issues or concerns.',
    icon: ScaleIcon,
    resultTitle: 'Legal Analysis'
  },
  {
    id: 'translate',
    label: 'Translate Document',
    description: 'Translate the document to another language while preserving context',
    prompt: 'Please translate this document to French while maintaining its meaning and context.',
    icon: LanguagesIcon,
    resultTitle: 'Translated Content'
  }
];

type ActionResult = {
  id: string;
  content: string;
  status: 'completed' | 'processing' | 'error';
  createdAt: Date;
};

const DocumentActions: React.FC = () => {
  const { 
    currentDocument, 
    documentAnalysis, 
    isLoading, 
    sendChatMessage, 
    refreshDocumentAnalysis,
    chatMessages
  } = useDocumentContext();
  
  const [activeAction, setActiveAction] = useState<string | null>(null);
  const [processingAction, setProcessingAction] = useState<boolean>(false);
  const [actionResults, setActionResults] = useState<Record<string, ActionResult>>({});
  const [analysisProgress, setAnalysisProgress] = useState<number>(0);

  // Handle document analysis status
  const isAnalysisReady = documentAnalysis && documentAnalysis.status === 'completed';
  const isAnalysisProcessing = documentAnalysis && (documentAnalysis.status === 'processing' || documentAnalysis.status === 'pending');
  const isAnalysisFailed = documentAnalysis && (documentAnalysis.status === 'failed' || documentAnalysis.status === 'error');

  // Simulate progress for analysis
  React.useEffect(() => {
    let timer: NodeJS.Timeout;
    
    if (isAnalysisProcessing) {
      setAnalysisProgress(0);
      
      timer = setInterval(() => {
        setAnalysisProgress(prev => {
          const nextProgress = prev + Math.random() * 15;
          return nextProgress >= 90 ? 90 : nextProgress;
        });
      }, 1000);
    } else if (isAnalysisReady) {
      setAnalysisProgress(100);
    } else if (isAnalysisFailed) {
      setAnalysisProgress(0);
    }
    
    return () => {
      if (timer) clearInterval(timer);
    };
  }, [isAnalysisProcessing, isAnalysisReady, isAnalysisFailed]);

  // Monitor chat messages for results
  React.useEffect(() => {
    if (!activeAction || !processingAction || chatMessages.length === 0) return;
    
    // Look for the last system message that could be our response
    const lastSystemMessage = [...chatMessages]
      .reverse()
      .find(msg => msg.role === 'system');
      
    if (lastSystemMessage && lastSystemMessage.content) {
      // Update with the completed result
      setActionResults(prev => ({
        ...prev,
        [activeAction]: {
          id: activeAction,
          content: lastSystemMessage.content,
          status: 'completed',
          createdAt: new Date()
        }
      }));
      
      setProcessingAction(false);
    }
  }, [chatMessages, activeAction, processingAction]);

  const handleActionSelect = async (actionId: string) => {
    if (isLoading || processingAction || !isAnalysisReady) return;
    
    const action = documentActions.find(act => act.id === actionId);
    if (!action) return;
    
    setActiveAction(actionId);
    setProcessingAction(true);
    
    // Create a temporary result with processing status
    setActionResults(prev => ({
      ...prev,
      [actionId]: {
        id: actionId,
        content: 'Processing your request...',
        status: 'processing',
        createdAt: new Date()
      }
    }));
    
    try {
      // Send the action prompt to the chat system
      await sendChatMessage(action.prompt);
      
      // Note: The result will be updated by the useEffect above that monitors chat messages
    } catch (error) {
      console.error(`Error processing action ${actionId}:`, error);
      
      // Update with error result
      setActionResults(prev => ({
        ...prev,
        [actionId]: {
          id: actionId,
          content: 'An error occurred while processing your request. Please try again.',
          status: 'error',
          createdAt: new Date()
        }
      }));
      
      setProcessingAction(false);
    }
  };

  // Reset the active action and return to actions list
  const handleBackToActions = () => {
    setActiveAction(null);
  };

  return (
    <div className="flex flex-col h-full rounded-2xl border bg-card animate-fade-in shadow-sm overflow-hidden">
      <div className="border-b bg-muted/20 p-4">
        <h2 className="text-lg font-medium">Document Actions</h2>
        <p className="text-sm text-muted-foreground">
          Select an action to process your document
        </p>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        {!currentDocument ? (
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
        ) : !documentAnalysis ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-orange-100 p-3 rounded-full">
              <AlertCircleIcon className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h3 className="font-medium">Document needs analysis</h3>
              <p className="text-sm text-muted-foreground">
                Your document needs to be analyzed before actions can be performed
              </p>
            </div>
            <Button
              variant="default"
              size="sm"
              onClick={refreshDocumentAnalysis}
              disabled={isLoading}
            >
              <ScanIcon className="h-4 w-4 mr-2" />
              Start Analysis
            </Button>
          </div>
        ) : isAnalysisProcessing ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-4">
            <div className="bg-blue-100 p-3 rounded-full">
              <FileTextIcon className="h-6 w-6 text-blue-500 animate-pulse" />
            </div>
            <div>
              <h3 className="font-medium">Analyzing your document</h3>
              <p className="text-sm text-muted-foreground mb-2">
                Please wait while we prepare your document for actions
              </p>
              <Progress value={analysisProgress} className="w-64 h-2" />
              <p className="text-xs text-muted-foreground mt-2">
                {analysisProgress.toFixed(0)}% complete
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentAnalysis}
              disabled={isLoading}
            >
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              Check Progress
            </Button>
          </div>
        ) : isAnalysisFailed ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-red-100 p-3 rounded-full">
              <AlertCircleIcon className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <h3 className="font-medium">Analysis failed</h3>
              <p className="text-sm text-muted-foreground">
                {documentAnalysis?.error_message || "There was an error analyzing your document"}
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentAnalysis}
              disabled={isLoading}
            >
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              Retry Analysis
            </Button>
          </div>
        ) : activeAction ? (
          // Show action result
          <div className="h-full flex flex-col space-y-4">
            <div className="flex items-center justify-between">
              <Button
                variant="ghost"
                size="sm"
                onClick={handleBackToActions}
                className="px-2"
              >
                <ArrowRightIcon className="h-4 w-4 mr-2 rotate-180" />
                Back to Actions
              </Button>
              
              {/* Action title */}
              <div className="flex items-center">
                {(() => {
                  const action = documentActions.find(a => a.id === activeAction);
                  const Icon = action?.icon as LucideIcon;
                  return (
                    <>
                      {Icon && <Icon className="h-4 w-4 mr-2" />}
                      <span className="font-medium">{action?.resultTitle || 'Result'}</span>
                    </>
                  );
                })()}
              </div>
              
              <div>
                {actionResults[activeAction]?.status === 'completed' && (
                  <Badge variant="outline" className="bg-green-50">
                    <CheckIcon className="h-3 w-3 mr-1" />
                    Complete
                  </Badge>
                )}
                
                {actionResults[activeAction]?.status === 'processing' && (
                  <Badge variant="outline" className="bg-blue-50">
                    <RefreshCwIcon className="h-3 w-3 mr-1 animate-spin" />
                    Processing
                  </Badge>
                )}
                
                {actionResults[activeAction]?.status === 'error' && (
                  <Badge variant="outline" className="bg-red-50">
                    <AlertCircleIcon className="h-3 w-3 mr-1" />
                    Error
                  </Badge>
                )}
              </div>
            </div>
            
            {/* Result content */}
            <div className="flex-1 p-4 bg-background rounded-lg border overflow-auto whitespace-pre-wrap">
              {actionResults[activeAction]?.content || 'Processing your request...'}
            </div>
            
            {/* Actions for result */}
            <div className="flex justify-end space-x-2">
              <Button
                variant="outline"
                size="sm"
                onClick={() => handleActionSelect(activeAction)}
                disabled={processingAction || isLoading}
              >
                <RefreshCwIcon className="h-4 w-4 mr-2" />
                Regenerate
              </Button>
              {/* Additional actions like copy, download, etc. could be added here */}
            </div>
          </div>
        ) : (
          // Show available actions
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {documentActions.map((action) => {
              const Icon = action.icon;
              const hasResult = actionResults[action.id];
              
              return (
                <Card 
                  key={action.id}
                  className={`cursor-pointer transition-all hover:shadow-md ${
                    hasResult ? 'border-primary/20 bg-primary/5' : ''
                  }`}
                  onClick={() => handleActionSelect(action.id)}
                >
                  <CardHeader className="p-4 pb-2">
                    <div className="flex justify-between items-start">
                      <div className="bg-primary/10 p-2 rounded-full">
                        <Icon className="h-4 w-4 text-primary" />
                      </div>
                      
                      {hasResult && (
                        <Badge variant="outline" className="bg-green-50">
                          <CheckIcon className="h-3 w-3 mr-1" />
                          Done
                        </Badge>
                      )}
                    </div>
                    <CardTitle className="text-base mt-2">{action.label}</CardTitle>
                  </CardHeader>
                  <CardContent className="p-4 pt-0">
                    <CardDescription>{action.description}</CardDescription>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default DocumentActions;
