from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class DocumentUploadResponse(BaseModel):
    document_id: str
    filename: str
    status: str
    message: str
    file_size: int
    page_count: Optional[int] = None
    word_count: Optional[int] = None


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    document_ids: Optional[List[str]] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    sources: List[Dict[str, Any]] = Field(default_factory=list)
    conversation_id: str
    message_id: str


class DocumentInfo(BaseModel):
    id: str
    filename: str
    upload_date: datetime
    status: str
    page_count: Optional[int] = None
    word_count: Optional[int] = None
    file_size: int


class HealthCheckResponse(BaseModel):
    status: str
    service: str
    version: str
    database_connected: bool
    llm_connected: Optional[bool] = None
    embeddings_connected: Optional[bool] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
