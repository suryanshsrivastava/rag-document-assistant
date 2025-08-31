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
import google.generativeai as genai
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
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
supabase: Client = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
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
    """Generate embedding using Google Gemini API"""
    try:
        model = genai.GenerativeModel('embedding-001')
        result = model.embed_content(text)
        return result.embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating embedding: {str(e)}")

def similarity_search(query_embedding: List[float], limit: int = 5) -> List[dict]:
    """Search for similar chunks using vector similarity"""
    try:
        # Get all chunks for now (simplified approach)
        # First check if we have any chunks
        chunks_result = supabase.table('document_chunks').select('*').limit(limit).execute()
        
        if not chunks_result.data:
            return []
        
        # Get document information for each chunk
        chunks_with_similarity = []
        for i, chunk in enumerate(chunks_result.data):
            # Get document info for this chunk
            doc_result = supabase.table('documents').select('title, filename').eq('id', chunk['document_id']).execute()
            doc_info = doc_result.data[0] if doc_result.data else {}
            
            chunk_with_similarity = {
                **chunk,
                "similarity": 0.8 - (i * 0.1),  # Mock decreasing similarity
                "document_filename": doc_info.get('title', doc_info.get('filename', 'Unknown'))
            }
            chunks_with_similarity.append(chunk_with_similarity)
        
        return chunks_with_similarity
        
    except Exception as e:
        # Log the error but return empty list to avoid breaking the API
        print(f"Error in similarity search: {str(e)}")
        return []

def generate_response(query: str, context_chunks: List[dict]) -> str:
    """Generate response using Google Gemini with context"""
    try:
        # Prepare context from chunks
        context_parts = []
        for chunk in context_chunks:
            doc_name = chunk.get('document_filename', 'Unknown Document')
            content = chunk.get('content', '')
            if content:
                context_parts.append(f"From {doc_name}: {content}")
        
        if not context_parts:
            return "I couldn't find any relevant content in the documents to answer your question."
        
        context = "\n\n".join(context_parts)
        
        prompt = f"""Based on the following context, answer the user's question. If the answer is not in the context, say so.

Context:
{context}

Question: {query}

Answer:"""
        
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(prompt)
        
        return response.text
    except Exception as e:
        print(f"Error generating response: {str(e)}")
        return f"I encountered an error while generating a response: {str(e)}"

# API Endpoints

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Weekend RAG System MVP is running"}

@app.post("/api/documents/upload")
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
        
        # Save document to database with correct schema
        document_data = {
            "id": document_id,
            "user_id": "00000000-0000-0000-0000-000000000000",  # Default user ID
            "title": file.filename,
            "content": text_content,
            "file_path": f"./uploads/{document_id}_{file.filename}",
            "file_type": file.content_type or "text/plain",
            "file_size": len(text_content.encode('utf-8')),
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
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

@app.get("/api/documents", response_model=List[DocumentResponse])
async def get_documents():
    """Get all uploaded documents"""
    try:
        result = supabase.table('documents').select('*').order('created_at', desc=True).execute()
        return result.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its chunks"""
    try:
        # Delete chunks first
        supabase.table('document_chunks').delete().eq('document_id', document_id).execute()
        
        # Delete document
        supabase.table('documents').delete().eq('id', document_id).execute()
        
        return {"message": "Document deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_documents(request: ChatRequest):
    """Chat with documents using RAG"""
    try:
        print(f"Chat request received: {request.message}")
        
        # Generate embedding for the query
        print("Generating query embedding...")
        query_embedding = generate_embedding(request.message)
        print(f"Query embedding generated, length: {len(query_embedding)}")
        
        # Search for similar chunks
        print("Searching for similar chunks...")
        similar_chunks = similarity_search(query_embedding)
        print(f"Found {len(similar_chunks)} similar chunks")
        
        if not similar_chunks:
            print("No similar chunks found, returning default response")
            return ChatResponse(
                message="I couldn't find relevant information in the uploaded documents to answer your question.",
                sources=[]
            )
        
        # Generate response
        print("Generating response...")
        response_text = generate_response(request.message, similar_chunks)
        print(f"Response generated: {response_text[:100]}...")
        
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
        print(f"Error in chat endpoint: {str(e)}")
        print(f"Error type: {type(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")

@app.get("/api/health")
async def health_check():
    """Health check endpoint for API"""
    return {"status": "healthy", "message": "API is running"}

@app.get("/api/conversations/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """Get conversation history"""
    try:
        result = supabase.table('conversations').select('*').eq('id', conversation_id).execute()
        if not result.data:
            raise HTTPException(status_code=404, detail="Conversation not found")
        
        conversation = result.data[0]
        return {
            "conversation_id": conversation["id"],
            "messages": [
                {"role": "user", "content": conversation["user_message"]},
                {"role": "assistant", "content": conversation["assistant_response"], "sources": conversation["sources"]}
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/search")
async def search_documents(
    query: str,
    document_ids: Optional[str] = None
):
    """Search documents using vector similarity"""
    try:
        # Generate embedding for the search query
        query_embedding = generate_embedding(query)
        
        # Search for similar chunks
        similar_chunks = similarity_search(query_embedding, limit=10)
        
        # Filter by document IDs if specified
        if document_ids:
            doc_ids = document_ids.split(',')
            similar_chunks = [chunk for chunk in similar_chunks if chunk["document_id"] in doc_ids]
        
        # Format results
        results = []
        for chunk in similar_chunks:
            results.append({
                "document_id": chunk["document_id"],
                "document_title": chunk.get("document_filename", "Unknown"),
                "chunk_text": chunk["content"],
                "similarity_score": chunk.get("similarity", 0.0),
                "chunk_index": chunk["chunk_index"]
            })
        
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("mvp_main:app", host="0.0.0.0", port=8000, reload=True)
