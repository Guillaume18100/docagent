import React from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";
import { 
  RefreshCwIcon, 
  DownloadIcon, 
  FileTextIcon,
  AlertCircleIcon
} from 'lucide-react';

const DocumentViewer: React.FC = () => {
  const { 
    documentPreview, 
    currentDocument, 
    isLoading, 
    refreshDocumentPreview 
  } = useDocumentContext();

  const handleDownload = async () => {
    if (!currentDocument || !documentPreview) return;
    
    try {
      const blob = await documentService.downloadDocument(currentDocument.id);
      
      // Create a download link and trigger the download
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      
      // Get file extension safely from mime type or use the original extension from filename or default to pdf
      let fileExtension = 'pdf';
      if (documentPreview.mime_type && documentPreview.mime_type.includes('/')) {
        fileExtension = documentPreview.mime_type.split('/')[1];
      } else if (currentDocument.name && currentDocument.name.includes('.')) {
        fileExtension = currentDocument.name.split('.').pop() || 'pdf';
      }
      
      a.download = `${currentDocument.name.split('.')[0]}_processed.${fileExtension}`;
      document.body.appendChild(a);
      a.click();
      
      // Clean up
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading document:', error);
      // Toast error handled by the API service
    }
  };

  return (
    <div className="flex flex-col h-full rounded-2xl border bg-card animate-fade-in shadow-sm overflow-hidden">
      <div className="flex items-center justify-between p-4 border-b bg-muted/20">
        <div>
          <h2 className="text-lg font-medium">Document Preview</h2>
          <p className="text-sm text-muted-foreground">
            View and download the generated document
          </p>
        </div>
        
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={refreshDocumentPreview}
            disabled={!currentDocument || isLoading}
          >
            <RefreshCwIcon className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          
          <Button
            variant="default"
            size="sm"
            onClick={handleDownload}
            disabled={!currentDocument || !documentPreview || isLoading}
          >
            <DownloadIcon className="h-4 w-4 mr-2" />
            Download
          </Button>
        </div>
      </div>
      
      <div className="flex-1 p-4 overflow-auto">
        {isLoading ? (
          <div className="space-y-4 animate-pulse">
            <Skeleton className="h-8 w-3/4" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-full" />
            <Skeleton className="h-4 w-2/3" />
            <Skeleton className="h-32 w-full mt-6" />
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
                Upload a document to see the preview here
              </p>
            </div>
          </div>
        ) : !documentPreview ? (
          <div className="h-full flex flex-col items-center justify-center text-center p-4 space-y-3">
            <div className="bg-orange-100 p-3 rounded-full">
              <AlertCircleIcon className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <h3 className="font-medium">Document is being processed</h3>
              <p className="text-sm text-muted-foreground">
                Please wait while we generate the document preview
              </p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={refreshDocumentPreview}
            >
              <RefreshCwIcon className="h-4 w-4 mr-2" />
              Check Status
            </Button>
          </div>
        ) : (
          <div className="prose prose-sm max-w-none">
            <div 
              className="bg-white p-6 rounded-lg shadow-sm border"
              dangerouslySetInnerHTML={{ __html: documentPreview.content }}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// Add the import here to avoid circular dependency
import { documentService } from '@/services/apiService';

export default DocumentViewer;
