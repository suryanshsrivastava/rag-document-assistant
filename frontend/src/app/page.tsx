'use client';

import React, { useState } from 'react';
import DocumentUpload from '../components/DocumentUpload';
import ChatInterface from '../components/ChatInterface';
import DocumentList from '../components/DocumentList';
import Notification from '../components/Notification';
import LLMProviderSelector from '../components/LLMProviderSelector';
import { DocumentUploadResponse } from '../types/api';

interface NotificationState {
  show: boolean;
  message: string;
  type: 'success' | 'error' | 'info';
}

export default function Home() {
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);
  const [notification, setNotification] = useState<NotificationState>({
    show: false,
    message: '',
    type: 'info',
  });

  const showNotification = (message: string, type: 'success' | 'error' | 'info' = 'info') => {
    setNotification({ show: true, message, type });
  };

  const hideNotification = () => {
    setNotification(prev => ({ ...prev, show: false }));
  };

  const handleUploadSuccess = (response: DocumentUploadResponse) => {
    showNotification(
      `Document "${response.filename}" uploaded successfully!`,
      'success'
    );
  };

  const handleUploadError = (error: string) => {
    showNotification(error, 'error');
  };

  const handleProviderChange = (provider: string, providerName: string) => {
    showNotification(`Switched to ${providerName}`, 'success');
  };

  const handleProviderError = (error: string) => {
    showNotification(error, 'error');
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
              </div>
              <h1 className="text-xl font-semibold text-gray-900 dark:text-white">
                RAG Document Assistant
              </h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <LLMProviderSelector
                onProviderChange={handleProviderChange}
                onError={handleProviderError}
              />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-[calc(100vh-8rem)]">
          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Upload Section */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <h2 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Upload Documents
              </h2>
              <DocumentUpload
                onUploadSuccess={handleUploadSuccess}
                onUploadError={handleUploadError}
              />
            </div>

            {/* Document List */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
              <DocumentList
                selectedDocumentIds={selectedDocumentIds}
                onDocumentSelect={setSelectedDocumentIds}
              />
            </div>
          </div>

          {/* Chat Area */}
          <div className="lg:col-span-3">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 h-full flex flex-col">
              {/* Chat Header */}
              <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-lg font-medium text-gray-900 dark:text-white">
                      Chat with Documents
                    </h2>
                    {selectedDocumentIds.length > 0 && (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        {selectedDocumentIds.length} document{selectedDocumentIds.length !== 1 ? 's' : ''} selected
                      </p>
                    )}
                  </div>
                  
                  {selectedDocumentIds.length === 0 && (
                    <div className="text-sm text-gray-500 dark:text-gray-400">
                      Select documents to chat with specific content
                    </div>
                  )}
                </div>
              </div>

              {/* Chat Interface */}
              <div className="flex-1">
                <ChatInterface
                  selectedDocumentIds={selectedDocumentIds}
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Notification */}
      {notification.show && (
        <Notification
          message={notification.message}
          type={notification.type}
          onClose={hideNotification}
        />
      )}
    </div>
  );
}
