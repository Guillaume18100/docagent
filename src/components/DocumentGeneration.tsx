import React, { useEffect, useState } from 'react';
import { toast } from 'react-hot-toast';
import { useDocumentContext } from '../contexts/DocumentContext';
import { useToast } from '../hooks/useToast';

const DocumentGeneration = () => {
  const { currentDocument } = useDocumentContext();
  const { toast } = useToast();
  const [title, setTitle] = useState("");
  const [prompt, setPrompt] = useState("");
  const [outputFormat, setOutputFormat] = useState("docx");
  const [isGenerating, setIsGenerating] = useState(false);
  const [generatedDocuments, setGeneratedDocuments] = useState([]);
  const [activeTab, setActiveTab] = useState("new");
  
  // Fetch existing generated documents and setup polling
  useEffect(() => {
    const fetchGeneratedDocuments = async () => {
      try {
        const documents = await generateApi.getGeneratedDocuments();
        setGeneratedDocuments(documents);
      } catch (error) {
        console.error('Error fetching generated documents:', error);
      }
    };
    
    fetchGeneratedDocuments();
    
    // Polling logic to refresh the list and check for completed documents
    const interval = setInterval(async () => {
      try {
        const documents = await generateApi.getGeneratedDocuments();
        
        // Compare with previous state to detect completed documents
        setGeneratedDocuments(prevDocs => {
          // Check if any document has changed from generating/pending to completed
          const newlyCompleted = documents.filter(newDoc => 
            newDoc.status === 'completed' && 
            prevDocs.some(oldDoc => oldDoc.id === newDoc.id && 
              (oldDoc.status === 'generating' || oldDoc.status === 'pending'))
          );
          
          // Show toast notification for newly completed documents
          newlyCompleted.forEach(doc => {
            toast({
              title: "Document Ready",
              description: `Your document "${doc.title}" is ready for download!`,
              duration: 5000,
            });
          });
          
          return documents;
        });
      } catch (error) {
        console.error('Error refreshing generated documents:', error);
      }
    }, 5000); // Check every 5 seconds
    
    return () => clearInterval(interval);
  }, [toast]);
  
  // ... rest of the existing code ...
};

export default DocumentGeneration; 