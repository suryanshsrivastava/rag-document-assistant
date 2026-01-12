import {
  DocumentUploadResponse,
  ChatRequest,
  ChatResponse,
  DocumentInfo,
  HealthCheckResponse,
  LLMProviderResponse,
  LLMProvidersListResponse,
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
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        errorData.detail || response.statusText,
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof ApiError) throw error;
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new ApiError('Unable to connect to server', 0, 'Network error');
    }
    throw new ApiError(
      `Network error: ${error instanceof Error ? error.message : 'Unknown'}`,
      0
    );
  }
}

export const api = {
  async healthCheck(): Promise<HealthCheckResponse> {
    return makeRequest<HealthCheckResponse>('/health');
  },

  async uploadDocument(file: File): Promise<DocumentUploadResponse> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiError(
        `Upload failed: ${errorData.detail || response.statusText}`,
        response.status,
        errorData.detail
      );
    }

    return await response.json();
  },

  async getDocuments(): Promise<DocumentInfo[]> {
    return makeRequest<DocumentInfo[]>('/api/documents');
  },

  async deleteDocument(documentId: string): Promise<{ message: string }> {
    return makeRequest<{ message: string }>(`/api/documents/${documentId}`, {
      method: 'DELETE',
    });
  },

  async chat(request: ChatRequest): Promise<ChatResponse> {
    return makeRequest<ChatResponse>('/api/chat', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  },

  async getLLMProviders(): Promise<LLMProvidersListResponse> {
    return makeRequest<LLMProvidersListResponse>('/api/llm/providers');
  },

  async getCurrentLLMProvider(): Promise<LLMProviderResponse> {
    return makeRequest<LLMProviderResponse>('/api/llm/current');
  },

  async switchLLMProvider(provider: string): Promise<LLMProviderResponse> {
    return makeRequest<LLMProviderResponse>('/api/llm/switch', {
      method: 'POST',
      body: JSON.stringify({ provider }),
    });
  },
};

export { ApiError };
