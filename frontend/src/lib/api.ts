import {
  DocumentUploadResponse,
  ChatRequest,
  ChatResponse,
  DocumentInfo,
  HealthCheckResponse,
} from '../types/api';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public detail?: string
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function makeRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      let errorDetail = 'An error occurred';
      let errorCode = response.status;
      
      try {
        const errorData = await response.json();
        errorDetail = errorData.detail || errorData.message || errorDetail;
        errorCode = errorData.status || response.status;
      } catch {
        errorDetail = response.statusText;
      }
      
      // Handle specific error cases
      switch (response.status) {
        case 400:
          errorDetail = `Bad request: ${errorDetail}`;
          break;
        case 401:
          errorDetail = 'Authentication required';
          break;
        case 403:
          errorDetail = 'Access denied';
          break;
        case 404:
          errorDetail = 'Resource not found';
          break;
        case 413:
          errorDetail = 'File too large. Maximum size is 10MB';
          break;
        case 422:
          errorDetail = `Validation error: ${errorDetail}`;
          break;
        case 429:
          errorDetail = 'Too many requests. Please try again later';
          break;
        case 500:
          errorDetail = 'Server error. Please try again later';
          break;
        case 503:
          errorDetail = 'Service temporarily unavailable';
          break;
        default:
          errorDetail = `Error ${response.status}: ${errorDetail}`;
      }
      
      throw new ApiError(errorDetail, errorCode, errorDetail);
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    
    // Handle network errors
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError(
        'Unable to connect to server. Please check your internet connection.',
        0,
        'Network error'
      );
    }
    
    throw new ApiError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown error'}`,
      0
    );
  }
}

export const api = {
  // Health check
  async healthCheck(): Promise<HealthCheckResponse> {
    return makeRequest<HealthCheckResponse>('/health');
  },

  // Document upload
  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const url = `${API_BASE_URL}/api/documents/upload`;
    
    try {
      const response = await fetch(url, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        let errorDetail = 'Upload failed';
        try {
          const errorData = await response.json();
          errorDetail = errorData.detail || errorData.message || errorDetail;
        } catch {
          errorDetail = response.statusText;
        }
        
        throw new ApiError(
          `Upload failed: ${errorDetail}`,
          response.status,
          errorDetail
        );
      }

      return await response.json();
    } catch (error) {
      if (error instanceof ApiError) {
        throw error;
      }
      throw new ApiError(
        `Upload error: ${error instanceof Error ? error.message : 'Unknown error'}`,
        0
      );
    }
  },

  // List documents
  async getDocuments(): Promise<DocumentInfo[]> {
    return makeRequest<DocumentInfo[]>('/api/documents');
  },

  // Delete document
  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return makeRequest<{ message: string }>(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
  },

  // Chat with documents
  async chat(request: ChatRequest): Promise<ChatResponse> {
    return makeRequest<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  // Get conversation history
  async getConversationHistory(conversationId: string): Promise<{
    conversation_id: string;
    messages: Array<{
      role: string;
      content: string;
      sources?: Array<Record<string, any>>;
    }>;
  }> {
    return makeRequest(`/api/conversations/${conversationId}`);
  },

  // Search documents
  async searchDocuments(
    query: string,
    documentIds?: string[]
  ): Promise<Array<{
    document_id: string;
    document_title: string;
    chunk_text: string;
    similarity_score: number;
    chunk_index: number;
  }>> {
    const params = new URLSearchParams({ query });
    if (documentIds && documentIds.length > 0) {
      params.append('document_ids', documentIds.join(','));
    }
    
    return makeRequest(`/api/search?${params.toString()}`);
  },
};

export { ApiError }; 