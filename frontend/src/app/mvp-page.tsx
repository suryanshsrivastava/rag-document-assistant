'use client'

import { useState } from 'react'

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

export default function MVPPage() {
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
  useState(() => {
    loadDocuments()
  })

  return (
    <div className="container mx-auto p-4 max-w-4xl">
      <h1 className="text-3xl font-bold mb-8 text-center">Weekend RAG System - MVP</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Document Upload Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Upload Documents</h2>
          
          <div className="mb-4">
            <input
              type="file"
              accept=".pdf,.txt"
              onChange={handleFileUpload}
              disabled={uploading}
              className="w-full p-2 border border-gray-300 rounded"
            />
            {uploading && <p className="text-blue-600 mt-2">Uploading and processing...</p>}
          </div>

          <div className="mb-4">
            <h3 className="font-medium mb-2">Uploaded Documents ({documents.length})</h3>
            <div className="max-h-40 overflow-y-auto">
              {documents.map((doc) => (
                <div key={doc.id} className="p-2 border-b border-gray-200 text-sm">
                  <div className="font-medium">{doc.filename}</div>
                  <div className="text-gray-600">{doc.chunk_count} chunks</div>
                </div>
              ))}
            </div>
          </div>

          <button
            onClick={loadDocuments}
            className="w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600"
          >
            Refresh Documents
          </button>
        </div>

        {/* Chat Section */}
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Chat with Documents</h2>
          
          <div className="mb-4 h-96 overflow-y-auto border border-gray-200 rounded p-4">
            {chatMessages.length === 0 ? (
              <p className="text-gray-500 text-center">Upload documents and start chatting!</p>
            ) : (
              chatMessages.map((msg, index) => (
                <div key={index} className={`mb-4 ${msg.type === 'user' ? 'text-right' : 'text-left'}`}>
                  <div className={`inline-block p-3 rounded-lg max-w-xs ${
                    msg.type === 'user' 
                      ? 'bg-blue-500 text-white' 
                      : 'bg-gray-200 text-gray-800'
                  }`}>
                    {msg.content}
                  </div>
                  {msg.sources && msg.sources.length > 0 && (
                    <div className="text-xs text-gray-500 mt-1">
                      Sources: {msg.sources.map(s => s.document_filename).join(', ')}
                    </div>
                  )}
                </div>
              ))
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
              className="flex-1 p-2 border border-gray-300 rounded-l"
            />
            <button
              onClick={handleChat}
              disabled={chatting || !currentMessage.trim()}
              className="bg-green-500 text-white px-4 py-2 rounded-r hover:bg-green-600 disabled:bg-gray-400"
            >
              {chatting ? 'Sending...' : 'Send'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
