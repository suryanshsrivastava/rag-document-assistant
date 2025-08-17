# RAG System Backend

A FastAPI-based backend for a Retrieval-Augmented Generation (RAG) document assistant system.

## 🏗️ Architecture

The backend is built with the following components:

- **FastAPI**: Web framework for API endpoints
- **Supabase**: PostgreSQL database with vector storage
- **Google Gemini**: Embeddings and chat completions
- **Document Processing**: PDF, DOCX, and text file support

## 📁 Project Structure

```
backend/
├── app/
│   ├── main.py                 # FastAPI application and endpoints
│   ├── database/
│   │   ├── connection.py       # Supabase database connection
│   │   └── models.py          # Pydantic models for API schemas
│   └── services/
│       ├── document_processor.py  # File processing and text extraction
│       ├── chunking_service.py    # Text chunking with overlap
│       ├── gemini_client.py       # Google Gemini API integration
│       ├── vector_store.py        # Vector storage and similarity search
│       └── rag_service.py         # Main RAG orchestration
├── requirements.txt            # Python dependencies
├── test_backend.py            # Backend testing script
└── README.md                  # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory:

```env
# Supabase Configuration
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Set Up Database

Create the following tables in your Supabase database:

#### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    page_count INTEGER,
    word_count INTEGER,
    status TEXT DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Document Chunks Table
```sql
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536), -- Gemini embedding-001 dimension (updated to 1536)
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index for similarity search
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);
```

#### Conversations Table
```sql
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

#### Chat Messages Table
```sql
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4. Test the Backend

```bash
python test_backend.py
```

### 5. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 🔧 API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check with connection status

### Document Management
- `POST /api/documents/upload` - Upload and process a document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{document_id}` - Delete a document

### Chat and RAG
- `POST /api/chat` - Chat with documents using RAG
- `GET /api/conversations/{conversation_id}` - Get conversation history

### Search
- `GET /api/search` - Search across documents

## 🛠️ Services

### Document Processor
- Validates uploaded files (PDF, DOCX, TXT)
- Extracts text content using appropriate libraries
- Handles file storage and metadata extraction

### Chunking Service
- Splits text into 1000-1500 character chunks
- Maintains 200 character overlap between chunks
- Preserves sentence boundaries for natural splits

### Gemini Client
- Generates embeddings using `models/embedding-001`
- Creates chat completions using Gemini 2.0 Flash
- Handles rate limiting and batch processing

### Vector Store
- Stores embeddings in Supabase with pgvector
- Performs similarity search for relevant chunks
- Manages document chunk relationships

### RAG Service
- Orchestrates the complete RAG pipeline
- Coordinates document processing, chunking, embedding, and retrieval
- Handles conversation management

## 🔍 Testing

Run the test script to verify all components:

```bash
python test_backend.py
```

This will test:
- Module imports
- Service initialization
- Text chunking functionality
- Document validation
- Database connection (if configured)
- Gemini client (if API key provided)

## 📝 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `SUPABASE_URL` | Your Supabase project URL | Yes |
| `SUPABASE_ANON_KEY` | Your Supabase anonymous key | Yes |
| `GEMINI_API_KEY` | Your Google Gemini API key | Yes |

## 🚨 Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection**: Verify Supabase credentials and table setup

3. **Gemini API**: Check API key and rate limits

4. **File Upload**: Ensure upload directory exists and has write permissions

### Debug Mode

Enable debug logging by setting the log level:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 Development

### Adding New File Types

1. Update `DocumentProcessor.allowed_types`
2. Add extraction logic in `_extract_text()`
3. Update validation in `_validate_file()`

### Modifying Chunking Strategy

1. Adjust `chunk_size` and `overlap_size` in `ChunkingService`
2. Modify `_create_chunks_with_overlap()` for different strategies

### Extending Vector Search

1. Update similarity search in `VectorStore`
2. Add new metadata fields to chunks
3. Implement custom ranking algorithms

## 📚 Dependencies

Key dependencies include:
- `fastapi`: Web framework
- `supabase`: Database client
- `google-generativeai`: Google Gemini API client
- `PyPDF2`: PDF text extraction
- `python-docx`: DOCX text extraction
- `pydantic`: Data validation
- `python-multipart`: File upload handling

See `requirements.txt` for complete list. 