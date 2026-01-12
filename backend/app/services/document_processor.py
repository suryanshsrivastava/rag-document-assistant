"""Document processing service for extracting text from uploaded files."""

import os
import re
import uuid
import PyPDF2
import docx
from typing import Dict
from fastapi import UploadFile, HTTPException
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles file validation, storage, and text extraction from documents."""
    
    def __init__(self, upload_dir: str = "./uploads"):
        """Initialize with upload directory."""
        self.upload_dir = upload_dir
        self.allowed_types = {
            "application/pdf": [".pdf"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
            "text/plain": [".txt"]
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        os.makedirs(upload_dir, exist_ok=True)
    
    async def process_document(self, file: UploadFile) -> Dict:
        """Process uploaded file and return extracted text with metadata."""
        try:
            self._validate_file(file)
            file_path = self._save_file(file)
            text_content = self._extract_text(file_path, file.content_type)
            metadata = self._extract_metadata(file_path, file.content_type)
            metadata["word_count"] = self._count_words(text_content)
            
            return {
                "file_id": str(uuid.uuid4()),
                "filename": file.filename,
                "file_path": file_path,
                "text_content": text_content,
                "metadata": metadata,
                "status": "processed"
            }
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> None:
        """Validate file type, extension, and size."""
        if file.content_type not in self.allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        file_extension = os.path.splitext(file.filename)[1].lower()
        if file_extension not in self.allowed_types[file.content_type]:
            raise HTTPException(status_code=400, detail="File extension does not match content type")
        
        if file.size is None:
            raise HTTPException(status_code=400, detail="Unable to determine file size")
        
        if file.size > self.max_file_size:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {self.max_file_size / (1024*1024)}MB")
        
        if file.size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
    
    def _save_file(self, file: UploadFile) -> str:
        """Save uploaded file to disk with unique filename."""
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(self.upload_dir, unique_filename)
        
        with open(file_path, "wb") as buffer:
            content = file.file.read()
            buffer.write(content)
        
        logger.info(f"File saved: {file_path}")
        return file_path
    
    def _extract_text(self, file_path: str, content_type: str) -> str:
        """Extract text content from PDF, DOCX, or TXT files."""
        if content_type == "application/pdf":
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = "\n".join(page.extract_text() or "" for page in pdf_reader.pages)
                return self._clean_text(text)
        
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            doc = docx.Document(file_path)
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return self._clean_text(text)
        
        elif content_type == "text/plain":
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    return self._clean_text(file.read())
            except UnicodeDecodeError:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return self._clean_text(file.read())
        
        raise ValueError(f"Unsupported file type: {content_type}")
    
    def _extract_metadata(self, file_path: str, content_type: str) -> Dict:
        """Extract file size, page count, and timestamps."""
        return {
            "file_size": os.path.getsize(file_path),
            "content_type": content_type,
            "page_count": self._count_pages(file_path, content_type),
            "modification_time": os.path.getmtime(file_path),
            "created_at": datetime.now().isoformat()
        }
    
    def _clean_text(self, text: str) -> str:
        """Normalize whitespace and newlines."""
        if not text:
            return ""
        text = re.sub(r'[^\S\n]+', ' ', text)  # Collapse horizontal whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)  # Max 2 consecutive newlines
        return text.strip()
    
    def _count_pages(self, file_path: str, content_type: str) -> int:
        """Count pages in document (PDFs only, others return 1)."""
        if content_type == "application/pdf":
            with open(file_path, 'rb') as file:
                return len(PyPDF2.PdfReader(file).pages)
        return 1
    
    def _count_words(self, text: str) -> int:
        """Count words in text."""
        return len(text.split()) if text else 0
