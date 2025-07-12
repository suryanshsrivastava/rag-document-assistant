"""
MVP FastAPI Backend for Weekend RAG System
Simplified version focusing on core RAG functionality
"""

import os
import uuid
from datetime import datetime
from typing import List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import PyPDF2
import openai
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Weekend RAG System - MVP",
    description="Minimal viable product for document-based RAG system",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
openai.api_key = os.getenv("OPENAI_API_KEY")
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

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

# Helper functions
def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from PDF file"""
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error reading PDF: {str(e)}")
    return text

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
    """Split text into overlapping chunks"""
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
        
        if start >= len(text):
            break
    
    return chunks

def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    try:
        response = openai.embeddings.create(
            model="text-embedding-3-small",
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

def similarity_search(query_embedding: List[float], limit: int = 5) -> List[dict]:
    """Search for similar chunks using vector similarity"""
    try:
        # Use Supabase's vector search capability
        result = supabase.rpc('search_similar_chunks', {
            'query_embedding': query_embedding,
            'match_threshold': 0.7,
            'match_count': limit
        }).execute()
        
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in similarity search: {str(e)}")

def generate_response(query: str, context_chunks: List[dict]) -> str:
    """Generate response using OpenAI with context"""
    try:
        # Prepare context from chunks
        context = "\n\n".join([
            f"From {chunk['document_filename']}: {chunk['content']}"
            for chunk in context_chunks
        ])
        
        prompt = f"""Based on the following context, answer the user's question. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
        
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on provided documents."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Weekend RAG System MVP is running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a document"""
    try:
        # Validate file type
        if not file.filename.endswith(('.pdf', '.txt')):
            raise HTTPException(status_code=400, detail="Only PDF and TXT files are supported")
        
        # Generate unique ID
        document_id = str(uuid.uuid4())
        
        # Save file temporarily
        temp_path = f"/tmp/{document_id}_{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Extract text
        if file.filename.endswith('.pdf'):
            text_content = extract_text_from_pdf(temp_path)
        else:  # .txt file
            with open(temp_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
        
        # Clean up temp file
        os.remove(temp_path)
        
        # Chunk text
        chunks = chunk_text(text_content)
        
        # Save document to database
        document_data = {
            "id": document_id,
            "filename": file.filename,
            "content": text_content,
            "chunk_count": len(chunks),
            "created_at": datetime.utcnow().isoformat(),
            "processing_status": "completed"
        }
        
        supabase.table('documents').insert(document_data).execute()
        
        # Process and save chunks with embeddings
        for i, chunk in enumerate(chunks):
            embedding = generate_embedding(chunk)
            
            chunk_data = {
                "document_id": document_id,
                "chunk_index": i,
                "content": chunk,
                "embedding": embedding,
                "created_at": datetime.utcnow().isoformat()
            }
            
            supabase.table('document_chunks').insert(chunk_data).execute()
        
        return {
            "document_id": document_id,
            "filename": file.filename,
            "status": "completed",
            "message": f"Document processed successfully. {len(chunks)} chunks created."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all uploaded documents"""
    try:
        result = supabase.table('documents').select('*').order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with documents using RAG"""
    try:
        # Generate embedding for the query
        query_embedding = generate_embedding(request.message)
        
        # Search for similar chunks
        similar_chunks = similarity_search(query_embedding)
        
        if not similar_chunks:
            return ChatResponse(
                message="I couldn't find relevant information in the uploaded documents to answer your question.",
                sources=[]
            )
        
        # Generate response
        response_text = generate_response(request.message, similar_chunks)
        
        # Prepare sources
        sources = [
            {
                "document_id": chunk["document_id"],
                "document_filename": chunk["document_filename"],
                "chunk_index": chunk["chunk_index"],
                "similarity": chunk["similarity"],
                "content": chunk["content"][:200] + "..." if len(chunk["content"]) > 200 else chunk["content"]
            }
            for chunk in similar_chunks
        ]
        
        # Save conversation (simplified)
        conversation_data = {
            "id": str(uuid.uuid4()),
            "user_message": request.message,
            "assistant_response": response_text,
            "sources": sources,
            "created_at": datetime.utcnow().isoformat()
        }
        
        supabase.table('conversations').insert(conversation_data).execute()
        
        return ChatResponse(
            message=response_text,
            sources=sources
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("mvp_main:app", host="0.0.0.0", port=8000, reload=True)
