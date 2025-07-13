"""
Database Models for RAG System

Pydantic models for database schemas and API request/response validation.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

# Database Schema Models
class Document(BaseModel):
    """Document model for database storage."""
    id: str = Field(..., description="Unique document identifier")
    filename: str = Field(..., description="Original filename")
    file_path: str = Field(..., description="Path to stored file")
    content_type: str = Field(..., description="MIME type of the file")
    file_size: int = Field(..., description="File size in bytes")
    page_count: Optional[int] = Field(None, description="Number of pages")
    word_count: Optional[int] = Field(None, description="Number of words")
    status: str = Field(default="processing", description="Processing status")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class DocumentChunk(BaseModel):
    """Document chunk model for vector storage."""
    id: str = Field(..., description="Unique chunk identifier")
    document_id: str = Field(..., description="Reference to parent document")
    chunk_text: str = Field(..., description="Text content of the chunk")
    chunk_index: int = Field(..., description="Position of chunk in document")
    embedding: Optional[List[float]] = Field(None, description="Vector embedding")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Conversation(BaseModel):
    """Conversation model for chat history."""
    id: str = Field(..., description="Unique conversation identifier")
    title: Optional[str] = Field(None, description="Conversation title")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    """Chat message model."""
    id: str = Field(..., description="Unique message identifier")
    conversation_id: str = Field(..., description="Reference to conversation")
    role: str = Field(..., description="Message role (user/assistant)")
    content: str = Field(..., description="Message content")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents")
    created_at: datetime = Field(default_factory=datetime.utcnow)

# API Request/Response Models
class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    document_id: str
    filename: str
    status: str
    message: str
    file_size: int
    page_count: Optional[int] = None
    word_count: Optional[int] = None

class ChatRequest(BaseModel):
    """Request model for chat interactions."""
    message: str = Field(..., min_length=1, description="User message")
    document_ids: Optional[List[str]] = Field(None, description="Specific documents to search")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")

class ChatResponse(BaseModel):
    """Response model for chat interactions."""
    response: str = Field(..., description="AI response")
    sources: List[Dict[str, Any]] = Field(default_factory=list, description="Source documents")
    conversation_id: str = Field(..., description="Conversation identifier")
    message_id: str = Field(..., description="Message identifier")

class DocumentInfo(BaseModel):
    """Response model for document information."""
    id: str
    filename: str
    upload_date: datetime
    status: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    file_size: int

class SearchResult(BaseModel):
    """Model for search results."""
    document_id: str
    document_title: str
    chunk_text: str
    similarity_score: float
    chunk_index: int

class HealthCheckResponse(BaseModel):
    """Health check response model."""
    status: str
    service: str
    version: str
    database_connected: bool
    timestamp: datetime = Field(default_factory=datetime.utcnow) 