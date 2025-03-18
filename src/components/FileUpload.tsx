import React, { useState, useRef } from 'react';
import { useDocumentContext } from '@/context/DocumentContext';
import { documentService } from '@/services/apiService';
import { useToast } from "@/components/ui/use-toast";
import { Button } from "@/components/ui/button";
import { Progress } from "@/components/ui/progress";
import { UploadIcon, FileTextIcon, XIcon } from 'lucide-react';
import { UploadState } from '@/types';

const ALLOWED_FILE_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document', // docx
  'application/msword', // doc
  'text/plain', // txt
];

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const FileUpload: React.FC = () => {
  const { setCurrentDocument } = useDocumentContext();
  const { toast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
  });

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] || null;
    setUploadState({ isUploading: false, progress: 0, error: null });
    
    if (!file) {
      setSelectedFile(null);
      return;
    }
    
    // Validate file type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: 'Invalid file type. Please upload a PDF, DOCX, DOC, or TXT file.',
      });
      return;
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: 'File is too large. Maximum size is 10MB.',
      });
      return;
    }
    
    setSelectedFile(file);
  };

  const handleRemoveFile = () => {
    setSelectedFile(null);
    setUploadState({ isUploading: false, progress: 0, error: null });
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    
    setUploadState({
      isUploading: true,
      progress: 0,
      error: null,
    });
    
    try {
      // Simulating upload progress (in a real app, this would come from axios progress event)
      const progressInterval = setInterval(() => {
        setUploadState(prev => ({
          ...prev,
          progress: Math.min(prev.progress + 10, 90), // Cap at 90% until complete
        }));
      }, 300);
      
      const result = await documentService.uploadDocument(selectedFile);
      
      clearInterval(progressInterval);
      setUploadState({
        isUploading: false,
        progress: 100,
        error: null,
      });
      
      toast({
        title: "Success",
        description: "Document uploaded successfully",
      });
      
      // Set the current document
      setCurrentDocument({
        id: result.id,
        name: selectedFile.name,
        created_at: new Date().toISOString(),
        status: 'processing',
        file_type: selectedFile.type,
      });
      
      // Clear the file input
      setSelectedFile(null);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    } catch (error) {
      clearInterval(progressInterval);
      
      // Check if it's a connection error
      const isConnectionError = error instanceof Error && 
        (error.message.includes('Network Error') || 
         error.message.includes('Failed to fetch') ||
         error.message.includes('Could not connect to the server') ||
         error.message.includes('timeout'));
      
      setUploadState({
        isUploading: false,
        progress: 0,
        error: isConnectionError 
          ? 'Connection error: Unable to reach the server. Please check your network connection and try again.'
          : 'Failed to upload document. Please try again.',
      });
      
      toast({
        title: "Upload Error",
        description: isConnectionError 
          ? "Connection failed. Please check your network and try again." 
          : "Failed to upload document",
        variant: "destructive",
      });
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    
    const file = e.dataTransfer.files?.[0] || null;
    if (!file) return;
    
    // Validate file type
    if (!ALLOWED_FILE_TYPES.includes(file.type)) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: 'Invalid file type. Please upload a PDF, DOCX, DOC, or TXT file.',
      });
      return;
    }
    
    // Validate file size
    if (file.size > MAX_FILE_SIZE) {
      setUploadState({
        isUploading: false,
        progress: 0,
        error: 'File is too large. Maximum size is 10MB.',
      });
      return;
    }
    
    setSelectedFile(file);
  };

  return (
    <div className="w-full px-4 animate-fade-in">
      <div 
        className={`w-full p-8 rounded-2xl border-2 border-dashed transition-all duration-300 
          ${selectedFile ? 'border-primary/50 bg-primary/5' : 'border-muted-foreground/30 hover:border-primary/30 bg-secondary/50'}`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="flex flex-col items-center justify-center text-center space-y-4">
          {!selectedFile ? (
            <>
              <div className="bg-primary/10 p-3 rounded-full">
                <UploadIcon className="h-8 w-8 text-primary" />
              </div>
              <div className="space-y-1">
                <h3 className="font-medium text-lg text-foreground">Upload Document</h3>
                <p className="text-sm text-muted-foreground">
                  Drag and drop or click to upload a PDF, DOCX, DOC, or TXT file
                </p>
                <p className="text-xs text-muted-foreground">(Max file size: 10MB)</p>
              </div>
              <Button 
                onClick={() => fileInputRef.current?.click()}
                className="relative overflow-hidden group"
                variant="secondary"
                size="sm"
              >
                Choose File
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".pdf,.docx,.doc,.txt"
                  className="hidden"
                />
              </Button>
            </>
          ) : (
            <div className="w-full space-y-4">
              <div className="flex items-center justify-between bg-background p-3 rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className="bg-primary/10 p-2 rounded-md">
                    <FileTextIcon className="h-6 w-6 text-primary" />
                  </div>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium truncate max-w-[200px]">
                      {selectedFile.name}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                    </span>
                  </div>
                </div>
                <Button 
                  variant="ghost" 
                  size="icon" 
                  onClick={handleRemoveFile}
                  disabled={uploadState.isUploading}
                >
                  <XIcon className="h-4 w-4" />
                </Button>
              </div>
              
              {uploadState.error && (
                <div className="text-sm text-destructive">
                  {uploadState.error}
                </div>
              )}
              
              {uploadState.isUploading && (
                <div className="space-y-2">
                  <Progress value={uploadState.progress} className="h-2" />
                  <div className="text-xs text-muted-foreground text-right">
                    {uploadState.progress}%
                  </div>
                </div>
              )}
              
              <Button 
                onClick={handleUpload} 
                className="w-full"
                disabled={uploadState.isUploading}
              >
                {uploadState.isUploading ? 'Uploading...' : 'Upload Document'}
              </Button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default FileUpload;
