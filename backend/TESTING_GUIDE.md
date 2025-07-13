# Backend Testing Guide

This guide shows you how to test the RAG backend functionality without a frontend.

## 🚀 Quick Start

### 1. Activate Virtual Environment
```bash
cd backend
source venv/bin/activate
```

### 2. Set Up Environment Variables
Create a `.env` file in the backend directory:
```env
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key
OPENAI_API_KEY=your_openai_api_key
```

### 3. Start the Server
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🧪 Testing Methods

### Method 1: Using curl (Recommended)

#### Test Health Check
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

#### Test Document Upload
```bash
# Upload a PDF file
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_document.pdf"

# Upload a text file
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample.txt"
```

#### Test Chat with Documents
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "accept: application/json" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "document_ids": ["your_document_id_here"]
  }'
```

#### List Documents
```bash
curl http://localhost:8000/api/documents
```

### Method 2: Using Python Scripts

#### Test Document Processing
```python
import requests
import json

# Test health check
response = requests.get("http://localhost:8000/health")
print("Health Check:", response.json())

# Test document upload
with open("sample_document.pdf", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/api/documents/upload", files=files)
    print("Upload Response:", response.json())

# Test chat
chat_data = {
    "message": "What is this document about?",
    "document_ids": ["your_document_id_here"]
}
response = requests.post("http://localhost:8000/api/chat", json=chat_data)
print("Chat Response:", response.json())
```

### Method 3: Using FastAPI Interactive Docs

1. Start the server
2. Open browser to `http://localhost:8000/docs`
3. Use the interactive API documentation

## 📄 Sample Documents for Testing

### Create a Sample PDF
```bash
# Create a simple text file first
echo "This is a sample document for testing the RAG system. It contains information about artificial intelligence and machine learning. The document discusses various topics including natural language processing, computer vision, and deep learning techniques." > sample.txt

# Convert to PDF (if you have pandoc)
pandoc sample.txt -o sample_document.pdf
```

### Create a Sample Text File
```bash
cat > sample.txt << 'EOF'
Artificial Intelligence and Machine Learning

This document provides an overview of artificial intelligence and machine learning concepts.

Key Topics:
1. Natural Language Processing (NLP)
   - Text analysis and understanding
   - Language generation and translation
   - Sentiment analysis

2. Computer Vision
   - Image recognition and classification
   - Object detection and tracking
   - Image segmentation

3. Deep Learning
   - Neural networks and architectures
   - Training and optimization techniques
   - Applications in various domains

The field of AI continues to evolve rapidly with new breakthroughs in research and practical applications.
EOF
```

## 🔍 Step-by-Step Testing Process

### Step 1: Basic Functionality Test
```bash
# 1. Start server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Test health endpoint
curl http://localhost:8000/health

# 3. Check if server is running
curl http://localhost:8000/
```

### Step 2: Document Upload Test
```bash
# 1. Create a test document
echo "This is a test document for the RAG system." > test_doc.txt

# 2. Upload the document
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_doc.txt"

# 3. Check the response for document_id
```

### Step 3: Chat Test
```bash
# Use the document_id from the previous step
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "document_ids": ["document_id_from_step_2"]
  }'
```

### Step 4: List Documents Test
```bash
curl http://localhost:8000/api/documents
```

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure virtual environment is activated
   source venv/bin/activate
   
   # Reinstall dependencies
   pip install -r requirements.txt
   ```

2. **Database Connection Errors**
   - Check `.env` file has correct Supabase credentials
   - Verify database tables are created
   - Test connection with `python test_backend.py`

3. **Gemini API Errors**
   - Verify API key is correct
   - Check rate limits and billing
   - Test with simple embedding generation

4. **File Upload Errors**
   - Check file size (max 10MB)
   - Verify file type (PDF, DOCX, TXT)
   - Ensure upload directory exists

### Debug Mode
```bash
# Start with debug logging
uvicorn app.main:app --reload --log-level debug
```

## 📊 Expected Responses

### Health Check Response
```json
{
  "status": "healthy",
  "service": "RAG Document Assistant",
  "version": "1.0.0",
  "database_connected": true,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

### Document Upload Response
```json
{
  "document_id": "uuid-here",
  "filename": "sample_document.pdf",
  "status": "processed",
  "message": "Document uploaded and processed successfully",
  "file_size": 1024,
  "word_count": 150
}
```

### Chat Response
```json
{
  "response": "Based on the document content...",
  "sources": [
    {
      "chunk_id": "uuid-here",
      "document_id": "doc-uuid",
      "chunk_text": "Relevant text chunk...",
      "similarity_score": 0.85
    }
  ],
  "conversation_id": "conv-uuid",
  "message_id": "msg-uuid"
}
```

## 🎯 Testing Checklist

- [ ] Server starts without errors
- [ ] Health endpoint returns healthy status
- [ ] Document upload accepts PDF/DOCX/TXT files
- [ ] Document processing creates chunks and embeddings
- [ ] Chat endpoint generates responses with sources
- [ ] Database stores documents and chunks correctly
- [ ] Vector search finds relevant chunks
- [ ] Error handling works for invalid files
- [ ] API responses follow expected schema

## 🚀 Next Steps

After successful testing:
1. Set up proper environment variables
2. Create database tables in Supabase
3. Test with larger documents
4. Move to frontend development
5. Implement end-to-end testing 