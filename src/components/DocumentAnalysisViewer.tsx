import React from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { Badge } from "@/components/ui/badge";
import { 
  RefreshCwIcon, 
  FileTextIcon,
  AlertCircleIcon,
  BrainIcon,
  TagIcon,
  SmileIcon,
  UserIcon,
  Hash
} from 'lucide-react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { ScrollArea } from './ui/scroll-area';

const DocumentAnalysisViewer: React.FC = () => {
  const { 
    currentDocument, 
    documentAnalysis,
    isLoading, 
    refreshDocumentAnalysis 
  } = useDocumentContext();

  // Helper to determine status color
  const getStatusColor = (status: string | undefined) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'processing': return 'bg-blue-500';
      case 'pending': return 'bg-yellow-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  return (
    <div className="flex flex-col h-full rounded-2xl border bg-card animate-fade-in shadow-sm overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b bg-muted/20">
        <div>
          <h2 className="text-lg font-medium">Document Analysis</h2>
          <p className="text-sm text-muted-foreground">
            AI-powered insights from your document
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={refreshDocumentAnalysis}
            disabled={!currentDocument || isLoading}
          >
            <RefreshCwIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
        </div>
      </div>
      
      <ScrollArea className="flex-1 p-4">
        {isLoading ? (
          <div className="space-y-4 animate-pulse">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-4/5" />
          </div>
        ) : !currentDocument ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-muted p-3 rounded-full">
              <FileTextIcon className="h-6 w-6 text-muted-foreground" />
            </div>
            <div>
              <h3 className="font-medium">No document uploaded</h3>
              <p className="text-sm text-muted-foreground">
                Upload a document to see AI analysis here
              </p>
            </div>
          </div>
        ) : !documentAnalysis ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-orange-100 p-3 rounded-full">
              <AlertCircleIcon className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h3 className="font-medium">Analysis not available</h3>
              <p className="text-sm text-muted-foreground">
                The document hasn't been analyzed yet
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentAnalysis}
            >
              <BrainIcon className="h-4 w-4 mr-2" />
              Analyze Document
            </Button>
          </div>
        ) : documentAnalysis.status === 'processing' || documentAnalysis.status === 'pending' ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-blue-100 p-3 rounded-full">
              <BrainIcon className="h-6 w-6 text-blue-500 animate-pulse" />
            </div>
            <div>
              <h3 className="font-medium">Analysis in progress</h3>
              <p className="text-sm text-muted-foreground">
                Please wait while we analyze your document
              </p>
              <Badge 
                variant="outline" 
                className="mt-2"
              >
                <div className={`h-2 w-2 rounded-full mr-2 ${getStatusColor(documentAnalysis.status)}`}></div>
                {documentAnalysis.status}
              </Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentAnalysis}
            >
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              Check Status
            </Button>
          </div>
        ) : documentAnalysis.status === 'failed' ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-red-100 p-3 rounded-full">
              <AlertCircleIcon className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <h3 className="font-medium">Analysis failed</h3>
              <p className="text-sm text-muted-foreground">
                {documentAnalysis.error_message || "Something went wrong during analysis"}
              </p>
              <Badge 
                variant="outline" 
                className="mt-2 text-red-500"
              >
                <div className="h-2 w-2 rounded-full mr-2 bg-red-500"></div>
                Failed
              </Badge>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentAnalysis}
            >
              <BrainIcon className="h-4 w-4 mr-2" />
              Retry Analysis
            </Button>
          </div>
        ) : (
          <div className="space-y-6">
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <BrainIcon className="h-5 w-5 mr-2 text-primary" />
                  Summary
                </CardTitle>
                <CardDescription>AI-generated summary of the document</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm">{documentAnalysis.summary}</p>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <TagIcon className="h-5 w-5 mr-2 text-primary" />
                  Keywords
                </CardTitle>
                <CardDescription>Key terms extracted from the document</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {documentAnalysis.keywords.map((keyword, index) => (
                    <Badge key={index} variant="secondary">
                      {keyword}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <SmileIcon className="h-5 w-5 mr-2 text-primary" />
                  Sentiment
                </CardTitle>
                <CardDescription>Overall sentiment of the document</CardDescription>
              </CardHeader>
              <CardContent>
                <Badge 
                  className={
                    documentAnalysis.sentiment === 'positive' ? 'bg-green-100 text-green-800' :
                    documentAnalysis.sentiment === 'negative' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }
                >
                  {documentAnalysis.sentiment}
                </Badge>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <UserIcon className="h-5 w-5 mr-2 text-primary" />
                  Entities
                </CardTitle>
                <CardDescription>Named entities identified in the document</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {Object.entries(documentAnalysis.entities).map(([category, items], idx) => (
                    <div key={idx}>
                      <h4 className="text-sm font-medium mb-1 capitalize">{category}</h4>
                      <div className="flex flex-wrap gap-2">
                        {items.map((item, index) => (
                          <Badge key={index} variant="outline">
                            {item}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
            
            <Card>
              <CardHeader className="pb-2">
                <CardTitle className="text-lg flex items-center">
                  <Hash className="h-5 w-5 mr-2 text-primary" />
                  Topics
                </CardTitle>
                <CardDescription>Key topics discussed in the document</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-wrap gap-2">
                  {documentAnalysis.topics.map((topic, index) => (
                    <Badge key={index} variant="secondary" className="bg-primary/10">
                      {topic}
                    </Badge>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </ScrollArea>
    </div>
  );
};

export default DocumentAnalysisViewer; 