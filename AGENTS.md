# RAG Document Assistant - Agent Guidelines

## Commands
- **Backend**: `source .rag-document-assistant/bin/activate && cd backend && uvicorn app.main:app --reload`
- **Frontend**: `cd frontend && npm run dev`
- **Lint frontend**: `cd frontend && npm run lint`
- **Install backend deps**: `source .rag-document-assistant/bin/activate && uv pip install -r backend/requirements.txt`
- **Run E2E tests**: `cd frontend && npm run test:e2e` (requires both backend and frontend running)
- **Run full E2E suite**: `./run-e2e-tests.sh` (starts servers, runs tests, cleans up)

## Architecture
- **Backend**: FastAPI (`backend/app/`) - services pattern with `rag_service.py` orchestrating document processing, embeddings, and LLM
- **Frontend**: Next.js 15 + TypeScript + Tailwind (`frontend/src/`) - components in `components/`, API client in `lib/api.ts`
- **LLM Providers**: Switchable via `llm_provider.py` - supports LM Studio (local) and Gemini (cloud)
- **Vector Store**: FAISS (`backend/faiss_db/`) with local embeddings via sentence-transformers
- **Document Metadata**: JSON files in `backend/document_metadata/`

## Code Style
- **Backend**: async/await, Pydantic models, try/catch with logging, service layer pattern
- **Frontend**: TypeScript strict, React hooks, Tailwind CSS, types in `types/api.ts`
- **Naming**: snake_case (Python), camelCase (TypeScript), PascalCase (React components)
- **Error handling**: HTTPException with proper status codes, ApiError class in frontend
- **Constants**: Use `backend/app/services/constants.py` for magic numbers
