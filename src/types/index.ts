// Document types
export interface Document {
  id: string;
  name: string;
  created_at: string;
  status: 'processing' | 'ready' | 'failed';
  file_type: string;
}

// Document analysis type
export interface DocumentAnalysis {
  id: string;
  document: string;
  summary: string;
  keywords: string[];
  sentiment: string;
  entities: Record<string, string[]>;
  topics: string[];
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message: string | null;
  created_at: string;
}

// Chat message types
export interface ChatMessage {
  id: string;
  document_id: string;
  content: string;
  sender: 'user' | 'system';
  timestamp: string;
}

// Document preview type
export interface DocumentPreview {
  id: string;
  content: string;
  mime_type: string;
  version: number;
  last_updated: string;
}

// Upload state type
export interface UploadState {
  isUploading: boolean;
  progress: number;
  error: string | null;
}

// Document context type
export interface DocumentContextType {
  currentDocument: Document | null;
  documentPreview: DocumentPreview | null;
  documentAnalysis: DocumentAnalysis | null;
  chatMessages: ChatMessage[];
  isLoading: boolean;
  setCurrentDocument: (document: Document | null) => void;
  refreshDocumentPreview: () => Promise<void>;
  refreshDocumentAnalysis: () => Promise<void>;
  sendChatMessage: (message: string) => Promise<void>;
}
