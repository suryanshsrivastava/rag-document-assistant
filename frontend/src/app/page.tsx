'use client'

import { useState, useEffect } from 'react'

interface Document {
  id: string
  filename: string
  created_at: string
  chunk_count: number
}

interface ChatMessage {
  message: string
  sources: Array<{
    document_filename: string
    content: string
    similarity: number
  }>
}

export default function Home() {
  const [documents, setDocuments] = useState<Document[]>([])
  const [uploading, setUploading] = useState(false)
  const [chatMessages, setChatMessages] = useState<Array<{ type: 'user' | 'assistant', content: string, sources?: any[] }>>([])
  const [currentMessage, setCurrentMessage] = useState('')
  const [chatting, setChatting] = useState(false)

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch('http://localhost:8000/upload', {
        method: 'POST',
        body: formData,
      })

      if (response.ok) {
        const result = await response.json()
        alert(`Document uploaded successfully! ${result.message}`)
        loadDocuments()
      } else {
        const error = await response.json()
        alert(`Upload failed: ${error.detail}`)
      }
    } catch (error) {
      alert(`Upload failed: ${error}`)
    } finally {
      setUploading(false)
    }
  }

  const loadDocuments = async () => {
    try {
      const response = await fetch('http://localhost:8000/documents')
      if (response.ok) {
        const docs = await response.json()
        setDocuments(docs)
      }
    } catch (error) {
      console.error('Failed to load documents:', error)
    }
  }

  const handleChat = async () => {
    if (!currentMessage.trim()) return

    setChatting(true)
    const userMessage = currentMessage
    setCurrentMessage('')

    // Add user message to chat
    setChatMessages(prev => [...prev, { type: 'user', content: userMessage }])

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage,
        }),
      })

      if (response.ok) {
        const result = await response.json()
        setChatMessages(prev => [...prev, { 
          type: 'assistant', 
          content: result.message, 
          sources: result.sources 
        }])
      } else {
        const error = await response.json()
        setChatMessages(prev => [...prev, { 
          type: 'assistant', 
          content: `Error: ${error.detail}` 
        }])
      }
    } catch (error) {
      setChatMessages(prev => [...prev, { 
        type: 'assistant', 
        content: `Error: ${error}` 
      }])
    } finally {
      setChatting(false)
    }
  }

  // Load documents on component mount
  useEffect(() => {
    loadDocuments()
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto p-4 max-w-6xl">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Weekend RAG System</h1>
          <p className="text-gray-600">Upload documents and chat with them using AI</p>
        </div>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Document Upload Section */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">📄 Upload Documents</h2>
            
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select a PDF or TXT file:
              </label>
              <input
                type="file"
                accept=".pdf,.txt"
                onChange={handleFileUpload}
                disabled={uploading}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              {uploading && (
                <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                  <div className="flex items-center">
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                    <span className="text-blue-700">Uploading and processing document...</span>
                  </div>
                </div>
              )}
            </div>

            <div className="mb-6">
              <h3 className="font-medium mb-3 text-gray-700">
                📚 Uploaded Documents ({documents.length})
              </h3>
              <div className="max-h-48 overflow-y-auto border border-gray-200 rounded-lg">
                {documents.length === 0 ? (
                  <div className="p-4 text-center text-gray-500">
                    No documents uploaded yet
                  </div>
                ) : (
                  documents.map((doc) => (
                    <div key={doc.id} className="p-3 border-b border-gray-100 hover:bg-gray-50">
                      <div className="font-medium text-gray-800">{doc.filename}</div>
                      <div className="text-sm text-gray-600">
                        {doc.chunk_count} chunks • {new Date(doc.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            <button
              onClick={loadDocuments}
              className="w-full bg-blue-600 text-white py-3 px-4 rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              🔄 Refresh Documents
            </button>
          </div>

          {/* Chat Section */}
          <div className="bg-white p-6 rounded-lg shadow-md">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">💬 Chat with Documents</h2>
            
            <div className="mb-4 h-96 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
              {chatMessages.length === 0 ? (
                <div className="text-center text-gray-500 mt-20">
                  <div className="text-4xl mb-2">🤖</div>
                  <p>Upload documents and start chatting!</p>
                  <p className="text-sm mt-1">Ask questions about your uploaded documents</p>
                </div>
              ) : (
                chatMessages.map((msg, index) => (
                  <div key={index} className={`mb-4 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block p-3 rounded-lg max-w-xs lg:max-w-md ${
                      msg.type === 'user' 
                        ? 'bg-blue-600 text-white' 
                        : 'bg-white text-gray-800 border border-gray-200'
                    }`}>
                      {msg.content}
                    </div>
                    {msg.sources && msg.sources.length > 0 && (
                      <div className="text-xs text-gray-500 mt-1 ml-1">
                        📎 Sources: {msg.sources.map(s => s.document_filename).join(', ')}
                      </div>
                    )}
                  </div>
                ))
              )}
              {chatting && (
                <div className="text-left">
                  <div className="inline-block p-3 rounded-lg bg-gray-200 text-gray-800">
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-gray-600 mr-2"></div>
                      Thinking...
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="flex">
              <input
                type="text"
                value={currentMessage}
                onChange={(e) => setCurrentMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleChat()}
                placeholder="Ask a question about your documents..."
                disabled={chatting}
                className="flex-1 p-3 border border-gray-300 rounded-l-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              />
              <button
                onClick={handleChat}
                disabled={chatting || !currentMessage.trim()}
                className="bg-green-600 text-white px-6 py-3 rounded-r-lg hover:bg-green-700 disabled:bg-gray-400 transition-colors font-medium"
              >
                {chatting ? '⏳' : '📤'}
              </button>
            </div>
          </div>
        </div>

        {/* Status Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>Backend running in demo mode • Data is stored in memory</p>
          <p className="mt-1">
            <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer" 
               className="text-blue-600 hover:underline">
              View API Documentation
            </a>
          </p>
        </div>
      </div>
    </div>
  )
}
