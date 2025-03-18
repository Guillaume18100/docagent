import React from 'react';
import { DocumentProvider } from '@/context/DocumentContext';
import FileUpload from '@/components/FileUpload';
import ChatInterface from '@/components/ChatInterface';
import DocumentViewer from '@/components/DocumentViewer';
import DocumentAnalysisViewer from '@/components/DocumentAnalysisViewer';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

const Index: React.FC = () => {
  return (
    <DocumentProvider>
      <div className="min-h-screen flex flex-col bg-background text-foreground antialiased">
        <header className="border-b bg-card">
          <div className="container py-4 px-6 mx-auto">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-2xl font-semibold">Enterprise Document Automation</h1>
                <p className="text-sm text-muted-foreground">
                  Upload documents, specify requirements, and generate drafts
                </p>
              </div>
            </div>
          </div>
        </header>
        
        <main className="flex-1 container mx-auto px-6 py-8">
          <div className="grid grid-cols-1 gap-8 lg:grid-cols-2 xl:grid-cols-3">
            <div className="flex flex-col space-y-6">
              <div className="rounded-xl bg-card p-6 shadow-sm border">
                <h2 className="text-xl font-medium mb-4">Document Upload</h2>
                <FileUpload />
              </div>
              
              <div className="mt-4 rounded-xl bg-muted/30 p-6 border">
                <h3 className="text-lg font-medium mb-2">Supported Documents</h3>
                <ul className="list-disc list-inside text-sm text-muted-foreground space-y-1">
                  <li>PDF documents (.pdf)</li>
                  <li>Word documents (.docx, .doc)</li>
                  <li>Text files (.txt)</li>
                </ul>
                <Separator className="my-4" />
                <h3 className="text-lg font-medium mb-2">How It Works</h3>
                <ol className="list-decimal list-inside text-sm text-muted-foreground space-y-1">
                  <li>Upload your document</li>
                  <li>The system will automatically analyze your document</li>
                  <li>Specify your requirements in the chat</li>
                  <li>Review and download the generated draft</li>
                </ol>
              </div>
            </div>
            
            <div className="h-[700px]">
              <ChatInterface />
            </div>
            
            <div className="h-[700px]">
              <Tabs defaultValue="preview" className="h-full flex flex-col">
                <TabsList className="grid w-full grid-cols-2">
                  <TabsTrigger value="preview">Document Preview</TabsTrigger>
                  <TabsTrigger value="analysis">AI Analysis</TabsTrigger>
                </TabsList>
                <TabsContent value="preview" className="flex-1 mt-0">
                  <DocumentViewer />
                </TabsContent>
                <TabsContent value="analysis" className="flex-1 mt-0">
                  <DocumentAnalysisViewer />
                </TabsContent>
              </Tabs>
            </div>
          </div>
        </main>
        
        <footer className="border-t bg-muted/20">
          <div className="container mx-auto py-4 px-6">
            <p className="text-sm text-center text-muted-foreground">
              Enterprise Document Automation System — Prototype
            </p>
          </div>
        </footer>
      </div>
    </DocumentProvider>
  );
};

export default Index;
