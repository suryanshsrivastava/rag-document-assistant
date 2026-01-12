# RAG Document Assistant

A complete Retrieval-Augmented Generation (RAG) system that allows users to upload documents and have intelligent conversations with their content using AI.

## Features

- **Document Upload**: Support for PDF, DOCX, TXT, and Excel files with drag-and-drop interface
- **Intelligent Text Processing**: Automatic text extraction, chunking, and embedding generation
- **Vector Search**: Semantic search across document chunks using local FAISS vector store
- **AI Chat Interface**: Real-time conversations with document context
- **Multiple LLM Providers**: Switch between Google Gemini (cloud) and LM Studio (local)
- **Local Storage**: All data stored locally - FAISS vector store and document metadata
- **Document Management**: View, select, and manage uploaded documents
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Dark Mode**: Automatic dark/light mode support
- **E2E Testing**: Comprehensive Playwright test suite

## Architecture

### Backend (FastAPI)
- **Service Pattern**: Clean architecture with `rag_service.py` orchestrating document processing
- **Vector Store**: FAISS with local embeddings via sentence-transformers
- **LLM Providers**: Pluggable provider system supporting:
  - Google Gemini (cloud, requires API key)
  - LM Studio (local, OpenAI-compatible API)
- **Document Processing**: Chunking with configurable overlap and metadata storage

### Frontend (Next.js 15)
- **TypeScript**: Fully typed with strict mode
- **Components**: Modular React components with hooks
- **API Client**: Centralized API communication with error handling
- **Styling**: Tailwind CSS 4 with responsive design

## Quick Start

### Prerequisites

- Python 3.14+
- Node.js 20+
- (Optional) LM Studio running on `http://localhost:1234` for local LLM

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-document-assistant
```

2. Set up Python environment:
```bash
python3 -m venv .rag-document-assistant
source .rag-document-assistant/bin/activate
uv pip install -r backend/requirements.txt
```

3. Install frontend dependencies:
```bash
cd frontend
npm install
cd ..
```

4. Configure environment:
```bash
# Backend
cp backend/.env.example backend/.env  # If available, or create manually

# Frontend
cd frontend
cp .env.example .env.local  # If available
cd ..
```

### Running the Application

1. Start the backend:
```bash
source .rag-document-assistant/bin/activate
cd backend
uvicorn app.main:app --reload
```

2. Start the frontend (in a new terminal):
```bash
cd frontend
npm run dev
```

3. Open your browser:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Testing

### E2E Tests

The project includes comprehensive end-to-end tests using Playwright:

**Run tests (with servers running):**
```bash
cd frontend
npm run test:e2e
```

**Run full test suite (starts servers, runs tests, cleans up):**
```bash
./run-e2e-tests.sh
```

**Test coverage:**
- Backend health checks
- Document upload via API and UI
- Document listing and management
- Chat functionality with RAG
- LLM provider switching
- Complete user workflows

## LLM Provider Configuration

### Google Gemini (Default)
Requires `GEMINI_API_KEY` in backend environment variables.

### LM Studio (Local)
1. Download and install LM Studio
2. Run LM Studio and load a model
3. Start the server (defaults to `http://localhost:1234`)
4. Switch to LM Studio provider in the UI

The system will automatically fall back to Gemini if LM Studio is not available.

## API Endpoints

### Health & Providers
- `GET /health` - Service health check
- `GET /api/llm/providers` - List available LLM providers
- `GET /api/llm/current` - Get current provider
- `POST /api/llm/switch` - Switch LLM provider

### Documents
- `POST /api/documents/upload` - Upload and process document
- `GET /api/documents` - List all documents
- `DELETE /api/documents/{document_id}` - Delete document

### Chat
- `POST /api/chat` - Send message with optional document selection

## Project Structure

```
rag-document-assistant/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── database/
│   │   │   └── models.py         # Pydantic models
│   │   └── services/
│   │       ├── rag_service.py    # RAG orchestration
│   │       ├── llm_provider.py   # LLM provider management
│   │       ├── local_embeddings.py  # Local embeddings
│   │       ├── local_vector_store.py  # FAISS integration
│   │       ├── document_processor.py  # Document parsing
│   │       ├── chunking_service.py    # Text chunking
│   │       ├── gemini_client.py       # Gemini API
│   │       └── lmstudio_client.py     # LM Studio client
│   ├── faiss_db/                 # FAISS vector store
│   ├── document_metadata/        # Document metadata JSON
│   ├── uploads/                  # Uploaded files
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── page.tsx          # Main page
│   │   │   └── layout.tsx        # Root layout
│   │   ├── components/
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── DocumentUpload.tsx
│   │   │   ├── DocumentList.tsx
│   │   │   └── LLMProviderSelector.tsx
│   │   ├── lib/
│   │   │   ├── api.ts            # API client
│   │   │   ├── fileUtils.ts      # File utilities
│   │   │   ├── errorMessages.ts  # Error handling
│   │   │   └── constants.ts      # Constants
│   │   └── types/
│   │       └── api.ts            # TypeScript types
│   ├── e2e/
│   │   └── rag-pipeline.spec.ts  # E2E tests
│   ├── playwright.config.ts       # Playwright config
│   └── package.json
├── run-e2e-tests.sh              # E2E test runner
├── AGENTS.md                     # Development guidelines
└── README.md
```

## Development

### Backend
```bash
source .rag-document-assistant/bin/activate
cd backend
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm run dev
```

### Linting
```bash
# Frontend
cd frontend
npm run lint
```

## Notes

- All data is stored locally in FAISS and JSON files
- No external database required
- Document embeddings are generated using sentence-transformers
- Supports switching between cloud (Gemini) and local (LM Studio) LLM providers
