from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from dotenv import load_dotenv
import logging

from .services.rag_service import RAGService
from .services.llm_provider import LLMProvider
from .database.models import (
    DocumentUploadResponse,
    ChatRequest,
    ChatResponse,
    DocumentInfo,
    HealthCheckResponse,
)

load_dotenv()

app = FastAPI(
    title="RAG Document Assistant",
    description="AI-powered document conversations using RAG",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_service = RAGService()
logger = logging.getLogger(__name__)


class LLMProviderRequest(BaseModel):
    provider: str


class LLMProviderResponse(BaseModel):
    provider: Optional[str]
    provider_name: Optional[str]


class LLMProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    configured: bool
    config: dict


class LLMProvidersListResponse(BaseModel):
    providers: List[LLMProviderInfo]
    current: Optional[str]


@app.get("/")
async def root():
    return {"message": "RAG Document Assistant API is running"}


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    try:
        connection_status = await rag_service.test_all_connections()
        all_services_healthy = all(connection_status.values())
        status = "healthy" if all_services_healthy else "degraded"

        return HealthCheckResponse(
            status=status,
            service="RAG Document Assistant",
            version="1.0.0",
            database_connected=connection_status.get("vector_store", False),
            llm_connected=connection_status.get("llm", False),
            embeddings_connected=connection_status.get("embeddings", False),
            timestamp=datetime.utcnow(),
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service="RAG Document Assistant",
            version="1.0.0",
            database_connected=False,
            llm_connected=False,
            embeddings_connected=False,
            timestamp=datetime.utcnow(),
        )


@app.get("/api/llm/providers", response_model=LLMProvidersListResponse)
async def get_llm_providers():
    try:
        providers = rag_service.get_available_providers()
        current = rag_service.get_current_llm_provider()
        return LLMProvidersListResponse(
            providers=[LLMProviderInfo(**p) for p in providers],
            current=current.get("provider"),
        )
    except Exception as e:
        logger.error(f"Error getting LLM providers: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting LLM providers: {str(e)}"
        )


@app.get("/api/llm/current", response_model=LLMProviderResponse)
async def get_current_llm_provider():
    try:
        current = rag_service.get_current_llm_provider()
        return LLMProviderResponse(**current)
    except Exception as e:
        logger.error(f"Error getting current LLM provider: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error getting current LLM provider: {str(e)}"
        )


@app.post("/api/llm/switch", response_model=LLMProviderResponse)
async def switch_llm_provider(request: LLMProviderRequest):
    try:
        provider_str = request.provider.lower()
        try:
            provider = LLMProvider(provider_str)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider '{provider_str}'. Supported: lmstudio, gemini",
            )

        result = rag_service.switch_llm_provider(provider)

        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=f"Failed to switch provider: {result.get('error')}",
            )

        return LLMProviderResponse(
            provider=result["provider"],
            provider_name=result["provider_name"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error switching LLM provider: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error switching LLM provider: {str(e)}"
        )


@app.post("/api/llm/test")
async def test_llm_connection():
    try:
        connection_status = await rag_service.test_all_connections()
        current = rag_service.get_current_llm_provider()

        return {
            "provider": current.get("provider"),
            "provider_name": current.get("provider_name"),
            "connected": connection_status.get("llm", False),
        }
    except Exception as e:
        logger.error(f"Error testing LLM connection: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error testing LLM connection: {str(e)}"
        )


@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    try:
        result = await rag_service.process_document(file)

        return DocumentUploadResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            status=result["status"],
            message="Document uploaded and processed successfully",
            file_size=result["file_size"],
            word_count=result["word_count"],
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error processing document: {str(e)}"
        )


@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    try:
        documents = await rag_service.get_all_documents()
        return documents
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error listing documents: {str(e)}"
        )


@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    try:
        success = await rag_service.delete_document(document_id)

        if success:
            return {"message": f"Document {document_id} deleted successfully"}
        else:
            raise HTTPException(
                status_code=404,
                detail=f"Document {document_id} not found or could not be deleted",
            )

    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}")
        raise HTTPException(
            status_code=500, detail=f"Error deleting document: {str(e)}"
        )


@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    try:
        result = await rag_service.chat_with_documents(
            user_message=request.message,
            document_ids=request.document_ids,
            conversation_id=request.conversation_id,
        )

        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            conversation_id=result["conversation_id"],
            message_id=result["message_id"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")


@app.get("/api/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    raise HTTPException(
        status_code=501, detail="Conversation history retrieval is not implemented yet."
    )


@app.get("/api/search")
async def search_documents(query: str, document_ids: Optional[str] = None):
    raise HTTPException(
        status_code=501, detail="Semantic search is not implemented yet."
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
