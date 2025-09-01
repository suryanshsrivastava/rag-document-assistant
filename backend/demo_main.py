"""
Demo FastAPI Backend for Weekend RAG System
Mock version for immediate testing without external dependencies
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import time

# Initialize FastAPI app
app = FastAPI(
    title="Weekend RAG System - Demo",
    description="Demo version with mock responses for immediate testing",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage for demo
demo_documents = []
demo_conversations = []

# Pydantic models
class DocumentResponse(BaseModel):
    id: str
    filename: str
    created_at: str
    chunk_count: int

class ChatRequest(BaseModel):
    message: str
    document_ids: Optional[List[str]] = None

class ChatResponse(BaseModel):
    message: str
    sources: List[dict]

# Mock helper functions
def extract_text_from_pdf_mock(file_path: str) -> str:
    """Mock PDF text extraction"""
    return f"Mock extracted text from {file_path}. This is sample content that would normally be extracted from a PDF file. It contains multiple sentences and paragraphs that would be chunked for RAG processing."

def extract_text_from_txt_mock(file_path: str) -> str:
    """Mock TXT text extraction"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return "Mock text file content. This is sample content from a text file."

def chunk_text_mock(text: str, chunk_size: int = 500) -> List[str]:
    """Mock text chunking"""
    # Simple chunking by splitting into sentences
    sentences = text.split('. ')
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        if len(current_chunk + sentence) < chunk_size:
            current_chunk += sentence + ". "
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks if chunks else [text]

def generate_mock_response(query: str, documents: List[dict]) -> str:
    """Generate mock response based on query and documents"""
    if not documents:
        return "I don't have any documents to reference. Please upload some documents first."
    
    # Mock responses based on common queries
    query_lower = query.lower()
    
    if "what" in query_lower or "explain" in query_lower:
        return f"Based on the uploaded documents ({len(documents)} documents), here's what I found: The documents contain information that relates to your query about '{query}'. This is a mock response that would normally be generated using AI based on the document content."
    
    elif "how" in query_lower:
        return f"According to the documents, here's how to approach this: The process involves several steps that are outlined in the uploaded materials. This mock response shows how the system would provide step-by-step guidance."
    
    elif "when" in query_lower or "time" in query_lower:
        return f"The documents indicate timing information related to your query. This mock response would normally extract specific dates and times from the document content."
    
    elif "who" in query_lower or "person" in query_lower:
        return f"The documents mention several people or entities. This mock response would identify key individuals mentioned in the content."
    
    else:
        return f"I found relevant information in the documents related to '{query}'. This mock response demonstrates how the RAG system would provide contextual answers based on the uploaded content. The system analyzed {len(documents)} documents to provide this response."

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Weekend RAG System Demo is running!", "mode": "demo"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document (mock version)"""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Generate unique ID
        document_id = str(uuid.uuid4())
        
        # Save file temporarily for demo
        temp_path = f"/tmp/{document_id}_{file.filename}"
        try:
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        except:
            # If /tmp doesn't exist, create a local temp file
            temp_path = f"./{document_id}_{file.filename}"
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
        
        # Mock text extraction
        if file.filename.endswith('.pdf'):
            text_content = extract_text_from_pdf_mock(temp_path)
        else:  # .txt file
            text_content = extract_text_from_txt_mock(temp_path)
        
        # Clean up temp file
        try:
            os.remove(temp_path)
        except:
            pass
        
        # Mock chunking
        chunks = chunk_text_mock(text_content)
        
        # Store in demo memory
        document_data = {
            "id": document_id,
            "filename": file.filename,
            "content": text_content,
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow().isoformat(),
            "processing_status": "completed",
            "chunks": chunks
        }
        
        demo_documents.append(document_data)
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "completed",
            "message": f"Document processed successfully! {len(chunks)} chunks created. (Demo mode - using mock processing)"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo error: {str(e)}")

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all uploaded documents"""
    return [
        DocumentResponse(
            id=doc["id"],
            filename=doc["filename"],
            created_at=doc["created_at"],
            chunk_count=doc["chunk_count"]
        )
        for doc in demo_documents
    ]

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with documents using mock RAG"""
    try:
        # Mock processing delay
        time.sleep(0.5)
        
        if not demo_documents:
            return ChatResponse(
                message="Please upload some documents first before asking questions.",
                sources=[]
            )
        
        # Generate mock response
        response_text = generate_mock_response(request.message, demo_documents)
        
        # Mock sources
        sources = []
        for i, doc in enumerate(demo_documents[:3]):  # Show up to 3 sources
            sources.append({
                "document_id": doc["id"],
                "document_filename": doc["filename"],
                "chunk_index": i,
                "similarity": 0.85 - (i * 0.1),  # Mock similarity scores
                "content": doc["chunks"][0][:200] + "..." if len(doc["chunks"]) > 0 else "Mock content..."
            })
        
        # Store conversation
        conversation_data = {
            "id": str(uuid.uuid4()),
            "user_message": request.message,
            "assistant_response": response_text,
            "sources": sources,
            "created_at": datetime.utcnow().isoformat()
        }
        
        demo_conversations.append(conversation_data)
        
        return ChatResponse(
            message=response_text,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo chat error: {str(e)}")

@app.get("/demo/stats")
async def get_demo_stats():
    """Get demo statistics"""
    return {
        "mode": "demo",
        "documents_uploaded": len(demo_documents),
        "conversations_held": len(demo_conversations),
        "message": "This is a demo version. Upload documents and try asking questions!",
        "features": [
            "Document upload (PDF/TXT)",
            "Mock text extraction",
            "Mock chunking",
            "Mock similarity search",
            "Mock AI responses",
            "Real-time chat interface"
        ]
    }

if __name__ == "__main__":
    print("🚀 Starting Weekend RAG System Demo")
    print("📝 Upload documents and start chatting!")
    print("🔗 Frontend: http://localhost:3000")
    print("📊 API Docs: http://localhost:8000/docs")
    print("📈 Demo Stats: http://localhost:8000/demo/stats")
    uvicorn.run("demo_main:app", host="0.0.0.0", port=8000, reload=True)
