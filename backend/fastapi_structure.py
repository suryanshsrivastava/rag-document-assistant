# main.py - FastAPI Application Entry Point
from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
from typing import List, Optional
import os
from dotenv import load_dotenv

# Import your service modules
from services.document_service import DocumentService
from services.embedding_service import EmbeddingService
from services.rag_service import RAGService
from services.ai_agent_service import AIAgentService
from models.schemas import DocumentResponse, ChatRequest, ChatResponse, UploadResponse

load_dotenv()

app = FastAPI(
    title="Intelligent Document Workspace API",
    description="AI-powered document analysis and conversation system",
    version="1.0.0"
)

# CORS middleware for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup
security = HTTPBearer()

# Initialize services - these handle the core business logic
document_service = DocumentService()
embedding_service = EmbeddingService()
rag_service = RAGService()
ai_agent_service = AIAgentService()

# Authentication dependency - simplified for demo
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Extract user from JWT token - implement based on your auth strategy"""
    # For demo purposes, return a mock user
    return {"user_id": "demo_user", "email": "demo@example.com"}

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Intelligent Document Workspace API is running"}

@app.post("/documents/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    user = Depends(get_current_user)
):
    """
    Upload and process a document for RAG system
    This endpoint handles file validation, text extraction, chunking, and embedding generation
    """
    try:
        # Validate file type and size
        if not file.filename.endswith(('.pdf', '.txt', '.docx', '.md')):
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Process the document through your pipeline
        document_id = await document_service.process_document(
            file=file, 
            user_id=user["user_id"]
        )
        
        # Generate embeddings in the background
        await embedding_service.generate_embeddings(document_id)
        
        return UploadResponse(
            document_id=document_id,
            filename=file.filename,
            status="processing",
            message="Document uploaded successfully and processing has begun"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents(user = Depends(get_current_user)):
    """Retrieve all documents for the current user"""
    try:
        documents = await document_service.get_user_documents(user["user_id"])
        return documents
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(
    request: ChatRequest,
    user = Depends(get_current_user)
):
    """
    Main conversation endpoint - this is where RAG and AI agent capabilities combine
    The request includes the user's question and optionally specific document IDs to search
    """
    try:
        # Step 1: Use RAG service to find relevant document chunks
        relevant_chunks = await rag_service.retrieve_relevant_chunks(
            query=request.message,
            user_id=user["user_id"],
            document_ids=request.document_ids,
            top_k=5
        )
        
        # Step 2: Use AI agent to generate response with context
        response = await ai_agent_service.generate_response(
            user_message=request.message,
            relevant_chunks=relevant_chunks,
            conversation_history=request.conversation_history
        )
        
        # Step 3: Save conversation for context management
        await ai_agent_service.save_conversation_turn(
            user_id=user["user_id"],
            user_message=request.message,
            ai_response=response.message,
            sources=response.sources
        )
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/conversations/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    user = Depends(get_current_user)
):
    """Retrieve conversation history for context switching"""
    try:
        history = await ai_agent_service.get_conversation_history(
            conversation_id=conversation_id,
            user_id=user["user_id"]
        )
        return history
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

# ================================
# services/document_service.py - Document Processing Logic
# ================================

import aiofiles
import asyncio
from typing import Optional
import uuid
from datetime import datetime
import PyPDF2
import docx
from supabase import create_client, Client
import os

class DocumentService:
    """Handles document upload, processing, and text extraction"""
    
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def process_document(self, file, user_id: str) -> str:
        """
        Main document processing pipeline
        1. Save file temporarily
        2. Extract text content
        3. Chunk the text for RAG
        4. Store in database
        """
        document_id = str(uuid.uuid4())
        
        # Save file temporarily for processing
        temp_path = f"/tmp/{document_id}_{file.filename}"
        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Extract text based on file type
        text_content = await self._extract_text(temp_path, file.filename)
        
        # Chunk the text for better RAG performance
        chunks = self._chunk_text(text_content)
        
        # Store document metadata
        document_data = {
            "id": document_id,
            "user_id": user_id,
            "filename": file.filename,
            "content": text_content,
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow().isoformat(),
            "processing_status": "completed"
        }
        
        # Insert into Supabase
        await self._store_document(document_data, chunks)
        
        # Clean up temporary file
        os.remove(temp_path)
        
        return document_id
    
    async def _extract_text(self, file_path: str, filename: str) -> str:
        """Extract text from different file formats"""
        if filename.endswith('.pdf'):
            return await self._extract_pdf_text(file_path)
        elif filename.endswith('.docx'):
            return await self._extract_docx_text(file_path)
        elif filename.endswith(('.txt', '.md')):
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                return await f.read()
        else:
            raise ValueError(f"Unsupported file type: {filename}")
    
    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF files"""
        text = ""
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from Word documents"""
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    
    def _chunk_text(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """
        Split text into overlapping chunks for better RAG performance
        Overlap ensures we don't lose context at chunk boundaries
        """
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            
            # Try to end at a sentence boundary
            if end < len(text):
                last_period = chunk.rfind('.')
                if last_period > chunk_size // 2:
                    end = start + last_period + 1
                    chunk = text[start:end]
            
            chunks.append(chunk.strip())
            start = end - overlap
            
        return chunks
    
    async def _store_document(self, document_data: dict, chunks: List[str]):
        """Store document and chunks in Supabase"""
        # Insert document
        result = self.supabase.table('documents').insert(document_data).execute()
        
        # Insert chunks
        chunk_data = []
        for i, chunk in enumerate(chunks):
            chunk_data.append({
                "document_id": document_data["id"],
                "chunk_index": i,
                "content": chunk,
                "created_at": datetime.utcnow().isoformat()
            })
        
        self.supabase.table('document_chunks').insert(chunk_data).execute()

# ================================
# services/embedding_service.py - Vector Embedding Generation
# ================================

import openai
from typing import List
import numpy as np
import asyncio

class EmbeddingService:
    """Handles vector embedding generation and storage"""
    
    def __init__(self):
        self.client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    async def generate_embeddings(self, document_id: str):
        """Generate embeddings for all chunks of a document"""
        # Get all chunks for the document
        chunks_result = self.supabase.table('document_chunks').select('*').eq('document_id', document_id).execute()
        chunks = chunks_result.data
        
        # Generate embeddings in batches to avoid rate limits
        batch_size = 10
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            await self._process_embedding_batch(batch)
    
    async def _process_embedding_batch(self, chunks: List[dict]):
        """Process a batch of chunks for embedding generation"""
        texts = [chunk['content'] for chunk in chunks]
        
        # Generate embeddings using OpenAI
        response = self.client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        # Update chunks with embeddings
        for chunk, embedding_data in zip(chunks, response.data):
            embedding_vector = embedding_data.embedding
            
            # Store embedding in Supabase (pgvector handles the vector storage)
            self.supabase.table('document_chunks').update({
                'embedding': embedding_vector
            }).eq('id', chunk['id']).execute()

# ================================
# models/schemas.py - Pydantic Models
# ================================

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class DocumentResponse(BaseModel):
    """Response model for document information"""
    id: str
    filename: str
    created_at: datetime
    chunk_count: int
    processing_status: str

class UploadResponse(BaseModel):
    """Response model for document upload"""
    document_id: str
    filename: str
    status: str
    message: str

class ChatRequest(BaseModel):
    """Request model for chat interactions"""
    message: str
    document_ids: Optional[List[str]] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None

class ChatResponse(BaseModel):
    """Response model for chat interactions"""
    message: str
    sources: List[Dict[str, Any]]
    conversation_id: str
    timestamp: datetime

class SourceInfo(BaseModel):
    """Information about document sources in responses"""
    document_id: str
    document_name: str
    chunk_index: int
    relevance_score: float
    excerpt: str