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
  sources: Array<Record<string, unknown>>;
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

export interface HealthCheckResponse {
  status: string;
  service: string;
  version: string;
  database_connected: boolean;
  llm_connected?: boolean;
  embeddings_connected?: boolean;
  timestamp: string;
}

export interface LLMProviderInfo {
  id: string;
  name: string;
  description: string;
  configured: boolean;
  config: Record<string, unknown>;
}

export interface LLMProviderResponse {
  provider: string | null;
  provider_name: string | null;
}

export interface LLMProvidersListResponse {
  providers: LLMProviderInfo[];
  current: string | null;
}
