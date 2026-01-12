import { ApiError } from './api';

export function getUserMessageForApiError(
  error: ApiError,
  context: 'chat' | 'upload'
): string {
  switch (error.status) {
    case 0:
      return context === 'chat'
        ? 'Unable to connect to server. Please check your internet connection and try again.'
        : 'Unable to connect to server. Please check your internet connection.';
    case 400:
      return context === 'chat'
        ? `Invalid request: ${error.message}`
        : `Invalid file: ${error.message}`;
    case 413:
      return context === 'chat'
        ? 'The file you uploaded is too large. Please try a smaller file.'
        : 'File too large. Maximum size is 10MB.';
    case 415:
      return 'Unsupported file type. Please upload PDF, DOCX, or TXT files.';
    case 429:
      return 'Too many requests. Please wait a moment and try again.';
    case 500:
      return 'Server error. Please try again later.';
    case 503:
      return 'Service temporarily unavailable. Please try again later.';
    default:
      return context === 'chat' ? `Error: ${error.message}` : error.message;
  }
}
