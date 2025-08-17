export interface Document {
  id: string;
  filename: string;
  file_path: string;
  content_type: string;
  file_size: number;
  page_count?: number;
  word_count?: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface DocumentChunk {
  id: string;
  document_id: string;
  chunk_text: string;
  chunk_index: number;
  embedding?: number[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface Conversation {
  id: string;
  title?: string;
  created_at: string;
  updated_at: string;
}

export interface ChatMessage {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant';
  content: string;
  sources: Array<Record<string, any>>;
  created_at: string;
}

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  status: string;
  message: string;
  file_size: number;
  page_count?: number;
  word_count?: number;
}

export interface ChatRequest {
  message: string;
  document_ids?: string[];
  conversation_id?: string;
}

export interface ChatResponse {
  response: string;
  sources: Array<Record<string, any>>;
  conversation_id: string;
  message_id: string;
}

export interface DocumentInfo {
  id: string;
  filename: string;
  upload_date: string;
  status: string;
  page_count?: number;
  word_count?: number;
  file_size: number;
}

export interface SearchResult {
  document_id: string;
  document_title: string;
  chunk_text: string;
  similarity_score: number;
  chunk_index: number;
}

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  database_connected: boolean;
  gemini_connected?: boolean;
  timestamp: string;
}

export interface ApiError {
  detail: string;
  status_code: number;
} 