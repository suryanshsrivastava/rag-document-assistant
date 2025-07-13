from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
from datetime import datetime
import logging

# Import implemented services
from .services.rag_service import RAGService
from .services.document_processor import DocumentProcessor
from .services.vector_store import VectorStore
from .services.gemini_client import GeminiClient
from .services.chunking_service import ChunkingService
from .database.models import Document, DocumentUploadResponse, ChatRequest, ChatResponse, DocumentInfo, HealthCheckResponse
from .database.connection import get_supabase_client, test_database_connection, is_database_available

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="RAG Document Assistant",
    description="An AI-powered system for intelligent document conversations using RAG",
    version="1.0.0"
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service with lazy loading
rag_service = RAGService()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Health check endpoint
@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG Document Assistant API is running"}

@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Detailed health check with connection status"""
    try:
        # Test database connection
        db_connected = await test_database_connection()
        
        # Test Gemini connection (only if service is initialized)
        gemini_connected = False
        try:
            if rag_service._initialized:
                gemini_connected = await rag_service.gemini_client.test_connection()
            else:
                # Try to initialize just the Gemini client for testing
                gemini_client = GeminiClient()
                gemini_connected = await gemini_client.test_connection()
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            gemini_connected = False
        
        # Determine overall status
        status = "healthy" if db_connected else "unhealthy"
        
        return HealthCheckResponse(
            status=status,
            service="RAG Document Assistant",
            version="1.0.0",
            database_connected=db_connected,
            gemini_connected=gemini_connected,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        return HealthCheckResponse(
            status="unhealthy",
            service="RAG Document Assistant",
            version="1.0.0",
            database_connected=False,
            gemini_connected=False,
            timestamp=datetime.utcnow()
        )

# Document management endpoints
@app.post("/api/documents/upload", response_model=DocumentUploadResponse)
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document for RAG
    
    This endpoint:
    1. Validates the uploaded file
    2. Extracts text content
    3. Chunks the text intelligently
    4. Generates embeddings
    5. Stores everything in the database
    """
    try:
        # Process document through RAG pipeline
        result = await rag_service.process_document(file)
        
        return DocumentUploadResponse(
            document_id=result["document_id"],
            filename=result["filename"],
            status=result["status"],
            message="Document uploaded and processed successfully",
            file_size=result["file_size"],
            word_count=result["word_count"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    List all uploaded documents
    
    TODO: Implement database query to fetch all documents
    """
    # TODO: Query database for documents
    # documents = await get_all_documents()
    
    # Placeholder response
    return [
        DocumentInfo(
            id="doc_1",
            filename="sample_document.pdf",
            upload_date="2024-01-01T00:00:00Z",
            status="processed",
            page_count=10,
            word_count=2500
        )
    ]

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """
    Delete a document and its embeddings
    
    TODO: Implement document deletion
    1. Remove from vector database
    2. Delete file from storage
    3. Remove metadata from database
    """
    # TODO: Implement deletion logic
    return {"message": f"Document {document_id} deleted successfully"}

# Chat and RAG endpoints
@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """
    Chat with documents using RAG
    
    This endpoint:
    1. Embeds the user query
    2. Searches for similar document chunks
    3. Generates a response using the retrieved context
    4. Saves the conversation if a conversation_id is provided
    """
    try:
        # Process chat through RAG service
        result = await rag_service.chat_with_documents(
            user_message=request.message,
            document_ids=request.document_ids,
            conversation_id=request.conversation_id
        )
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            conversation_id=result["conversation_id"],
            message_id=result["message_id"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in chat: {str(e)}")

@app.get("/api/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get conversation history
    
    TODO: Implement conversation history retrieval
    """
    # TODO: Query database for conversation history
    return {
        "conversation_id": conversation_id,
        "messages": [
            {
                "role": "user",
                "content": "Sample question",
                "timestamp": "2024-01-01T00:00:00Z"
            },
            {
                "role": "assistant",
                "content": "Sample response",
                "sources": [],
                "timestamp": "2024-01-01T00:01:00Z"
            }
        ]
    }

# Search endpoints
@app.get("/api/search")
async def search_documents(query: str, document_ids: Optional[str] = None):
    """
    Search across documents without generating a conversational response
    
    TODO: Implement semantic search
    """
    # TODO: Implement search functionality
    return {
        "query": query,
        "results": [
            {
                "document_id": "doc_1",
                "filename": "sample_document.pdf",
                "chunk_text": "Relevant text containing the search terms...",
                "relevance_score": 0.92,
                "page": 1
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
