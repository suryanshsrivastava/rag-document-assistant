// pages/_app.tsx - Next.js App Configuration
import { AppProps } from 'next/app'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { Toaster } from 'react-hot-toast'
import { AuthProvider } from '../contexts/AuthContext'
import '../styles/globals.css'

// Create a QueryClient instance for data fetching and caching
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
})

function MyApp({ Component, pageProps }: AppProps) {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Component {...pageProps} />
        <Toaster position="top-right" />
      </AuthProvider>
    </QueryClientProvider>
  )
}

export default MyApp

// pages/index.tsx - Main Application Page
import { useState } from 'react'
import Head from 'next/head'
import { DocumentUpload } from '../components/DocumentUpload'
import { ChatInterface } from '../components/ChatInterface'
import { DocumentList } from '../components/DocumentList'
import { useAuth } from '../hooks/useAuth'
import { useDocuments } from '../hooks/useDocuments'

export default function Home() {
  const { user, isLoading: authLoading } = useAuth()
  const { documents, isLoading: documentsLoading } = useDocuments()
  const [selectedDocuments, setSelectedDocuments] = useState<string[]>([])
  const [activeTab, setActiveTab] = useState<'upload' | 'chat' | 'documents'>('upload')

  if (authLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    )
  }

  return (
    <>
      <Head>
        <title>Intelligent Document Workspace</title>
        <meta name="description" content="AI-powered document analysis and conversation" />
      </Head>

      <div className="min-h-screen bg-gray-50">
        {/* Header Section */}
        <header className="bg-white shadow-sm border-b">
          <div className="max-w-7xl mx-auto px-4 py-4">
            <h1 className="text-2xl font-bold text-gray-900">
              Intelligent Document Workspace
            </h1>
            <p className="text-gray-600 mt-1">
              Upload documents and have intelligent conversations about their content
            </p>
          </div>
        </header>

        {/* Navigation Tabs */}
        <nav className="bg-white border-b">
          <div className="max-w-7xl mx-auto px-4">
            <div className="flex space-x-8">
              {[
                { id: 'upload', label: 'Upload Documents', icon: '📁' },
                { id: 'chat', label: 'Chat with Documents', icon: '💬' },
                { id: 'documents', label: 'My Documents', icon: '📋' }
              ].map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-2 border-b-2 font-medium text-sm ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          {activeTab === 'upload' && (
            <div className="max-w-2xl mx-auto">
              <DocumentUpload />
            </div>
          )}

          {activeTab === 'chat' && (
            <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
              {/* Document Selection Sidebar */}
              <div className="lg:col-span-1">
                <div className="bg-white rounded-lg shadow p-6">
                  <h3 className="text-lg font-medium mb-4">Select Documents</h3>
                  <DocumentSelector
                    documents={documents}
                    selectedDocuments={selectedDocuments}
                    onSelectionChange={setSelectedDocuments}
                  />
                </div>
              </div>

              {/* Chat Interface */}
              <div className="lg:col-span-3">
                <ChatInterface selectedDocuments={selectedDocuments} />
              </div>
            </div>
          )}

          {activeTab === 'documents' && (
            <div className="max-w-4xl mx-auto">
              <DocumentList documents={documents} isLoading={documentsLoading} />
            </div>
          )}
        </main>
      </div>
    </>
  )
}

// components/DocumentUpload.tsx - File Upload Component
import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { uploadDocument } from '../services/api'
import { UploadProgress } from './UploadProgress'

export function DocumentUpload() {
  const [uploadProgress, setUploadProgress] = useState<Record<string, number>>({})
  const queryClient = useQueryClient()

  const uploadMutation = useMutation({
    mutationFn: uploadDocument,
    onSuccess: (data, variables) => {
      toast.success(`Successfully uploaded ${variables.name}`)
      // Invalidate documents query to refresh the list
      queryClient.invalidateQueries({ queryKey: ['documents'] })
      // Remove from progress tracking
      setUploadProgress(prev => {
        const newProgress = { ...prev }
        delete newProgress[variables.name]
        return newProgress
      })
    },
    onError: (error, variables) => {
      toast.error(`Failed to upload ${variables.name}: ${error.message}`)
      setUploadProgress(prev => {
        const newProgress = { ...prev }
        delete newProgress[variables.name]
        return newProgress
      })
    }
  })

  const onDrop = useCallback((acceptedFiles: File[]) => {
    acceptedFiles.forEach(file => {
      // Start tracking upload progress
      setUploadProgress(prev => ({ ...prev, [file.name]: 0 }))
      
      // Create FormData for file upload
      const formData = new FormData()
      formData.append('file', file)
      
      uploadMutation.mutate(formData)
    })
  }, [uploadMutation])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'text/plain': ['.txt'],
      'text/markdown': ['.md'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxSize: 10 * 1024 * 1024 // 10MB limit
  })

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
          isDragActive
            ? 'border-blue-400 bg-blue-50'
            : 'border-gray-300 hover:border-gray-400'
        }`}
      >
        <input {...getInputProps()} />
        <div className="space-y-4">
          <div className="text-6xl">📄</div>
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragActive
                ? 'Drop the files here...'
                : 'Drag & drop files here, or click to select'
              }
            </p>
            <p className="text-gray-500 mt-2">
              Supports PDF, TXT, MD, and DOCX files (max 10MB)
            </p>
          </div>
        </div>
      </div>

      {/* Upload Progress */}
      {Object.keys(uploadProgress).length > 0 && (
        <div className="space-y-3">
          <h3 className="text-lg font-medium">Uploading Files</h3>
          {Object.entries(uploadProgress).map(([filename, progress]) => (
            <UploadProgress
              key={filename}
              filename={filename}
              progress={progress}
            />
          ))}
        </div>
      )}

      {/* Upload Instructions */}
      <div className="bg-blue-50 rounded-lg p-6">
        <h3 className="text-lg font-medium text