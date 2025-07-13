"""
Document Processor Service - Practice Template

This file contains the structure and TODO comments for implementing document processing.
Each TODO section includes hints and guidance based on the working MVP implementation.

Author: Your Name
Date: Today's Date
"""

import os
import uuid
import PyPDF2
import docx
from typing import Dict, List, Optional
from fastapi import UploadFile, HTTPException
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Service for processing uploaded documents and extracting text content.
    
    This class handles:
    - File validation and storage
    - Text extraction from different file types
    - Metadata extraction
    - Error handling
    """
    
    def __init__(self, upload_dir: str = "./uploads"):
        """
        Initialize the document processor.
        
        Args:
            upload_dir: Directory to store uploaded files
        """
        self.upload_dir = upload_dir
        self.allowed_types = {
            "application/pdf": [".pdf"],
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
            "text/plain": [".txt"]
        }
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        
        # Create upload directory if it doesn't exist
        os.makedirs(upload_dir, exist_ok=True)
    
    async def process_document(self, file: UploadFile) -> Dict:
        """
        Main document processing pipeline.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            Dict containing:
            - file_id: Unique identifier for the file
            - filename: Original filename
            - file_path: Path to saved file
            - text_content: Extracted text
            - metadata: Document metadata
            - status: Processing status
            
        Raises:
            HTTPException: If file validation fails or processing errors occur
        """
        try:
            # Step 1 - Validate the file
            self._validate_file(file)
            
            # Step 2 - Save the file
            file_path = self._save_file(file)
            
            # Step 3 - Extract text content
            text_content = self._extract_text(file_path, file.content_type)
            
            # Step 4 - Extract metadata
            metadata = self._extract_metadata(file_path, file.content_type)
            metadata["word_count"] = self._count_words(text_content)
            
            # Step 5 - Return structured result
            return {
                "file_id": str(uuid.uuid4()),
                "filename": file.filename,
                "file_path": file_path,
                "text_content": text_content,
                "metadata": metadata,
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file type and size.
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            bool: True if file is valid, False otherwise
            
        Raises:
            HTTPException: If file validation fails
        """
        # Check file type
        if file.content_type not in self.allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Check file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        allowed_extensions = self.allowed_types[file.content_type]
        if file_extension not in allowed_extensions:
            raise HTTPException(status_code=400, detail="File extension does not match content type")
        
        # Check file size
        if file.size is None:
            raise HTTPException(status_code=400, detail="Unable to determine file size")
        
        if file.size > self.max_file_size:
            raise HTTPException(status_code=400, detail=f"File too large. Maximum size is {self.max_file_size / (1024*1024)}MB")
        
        # Check if file has content
        if file.size == 0:
            raise HTTPException(status_code=400, detail="File is empty")
        
        return True
    
    def _save_file(self, file: UploadFile) -> str:
        """
        Save uploaded file to storage.
        
        TODO: Implement file saving logic:
        
        1. GENERATE UNIQUE FILENAME
           - Use UUID to ensure uniqueness
           - Preserve original file extension
           - Create safe filename (no special characters)
        
        2. SAVE FILE TO DISK
           - Write file content to upload directory
           - Handle file writing errors
           - Ensure file is completely written
        
        3. RETURN FILE PATH
           - Return full path to saved file
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            str: Full path to saved file
            
        Raises:
            Exception: If file saving fails
        """
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # Save file to disk
            with open(file_path, "wb") as buffer:
                content = file.file.read()
                buffer.write(content)
            
            logger.info(f"File saved successfully: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"Error saving file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")
    
    def _extract_text(self, file_path: str, content_type: str) -> str:
        """
        Extract text content from different file types.
        
        TODO: Implement text extraction for different file types:
        
        1. PDF FILES (application/pdf)
           - Use PyPDF2 to extract text
           - Handle encrypted PDFs
           - Extract text from all pages
           - Clean extracted text
        
        2. DOCX FILES (application/vnd.openxmlformats-officedocument.wordprocessingml.document)
           - Use python-docx library
           - Extract text from all paragraphs
           - Handle tables and other elements
        
        3. TEXT FILES (text/plain)
           - Read file content directly
           - Handle different encodings
           - Clean and normalize text
        
        4. TEXT CLEANING
           - Remove extra whitespace
           - Handle special characters
           - Normalize line endings
        
        Args:
            file_path: Path to the saved file
            content_type: MIME type of the file
            
        Returns:
            str: Extracted and cleaned text content
            
        Raises:
            Exception: If text extraction fails
        """
        try:
            if content_type == "application/pdf":
                # Extract text from PDF
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return self._clean_text(text)
            
            elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                # Extract text from DOCX
                doc = docx.Document(file_path)
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                return self._clean_text(text)
            
            elif content_type == "text/plain":
                # Extract text from plain text file
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        text = file.read()
                        return self._clean_text(text)
                except UnicodeDecodeError:
                    # Try with different encoding if UTF-8 fails
                    with open(file_path, 'r', encoding='latin-1') as file:
                        text = file.read()
                        return self._clean_text(text)
            
            else:
                raise Exception(f"Unsupported file type: {content_type}")
                
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {str(e)}")
            raise Exception(f"Text extraction failed: {str(e)}")
    
    def _extract_metadata(self, file_path: str, content_type: str) -> Dict:
        """
        Extract metadata from document.
        
        TODO: Implement metadata extraction:
        
        1. BASIC FILE INFO
           - File size
           - Creation date
           - Modification date
        
        2. DOCUMENT-SPECIFIC METADATA
           - Page count (for PDFs)
           - Word count
           - Character count
           - Title (if available)
           - Author (if available)
        
        3. CONTENT ANALYSIS
           - Language detection
           - Content type classification
           - Quality metrics
        
        Args:
            file_path: Path to the saved file
            content_type: MIME type of the file
            
        Returns:
            Dict: Metadata dictionary
        """
        try:
            # Get basic file info
            file_size = os.path.getsize(file_path)
            modification_time = os.path.getmtime(file_path)
            
            # Get document-specific metadata
            page_count = self._count_pages(file_path, content_type)
            
            metadata = {
                "file_size": file_size,
                "content_type": content_type,
                "page_count": page_count,
                "modification_time": modification_time,
                "created_at": datetime.now().isoformat()
            }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {file_path}: {str(e)}")
            return {
                "file_size": 0,
                "page_count": 0,
                "content_type": content_type
            }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize extracted text.
        
        TODO: Implement text cleaning:
        
        1. WHITESPACE NORMALIZATION
           - Remove extra spaces
           - Normalize line endings
           - Remove empty lines
        
        2. CHARACTER CLEANING
           - Remove special characters if needed
           - Handle unicode characters
           - Normalize quotes and dashes
        
        3. STRUCTURE PRESERVATION
           - Preserve paragraph breaks
           - Keep sentence boundaries
           - Maintain readability
        
        Args:
            text: Raw extracted text
            
        Returns:
            str: Cleaned and normalized text
        """
        # TODO: Implement text cleaning
        # HINT: Use regex to remove extra whitespace
        # HINT: Use .strip() to remove leading/trailing whitespace
        # HINT: Replace multiple newlines with single newlines
        
        # Example structure:
        # import re
        # text = re.sub(r'\s+', ' ', text)  # Replace multiple spaces with single space
        # text = re.sub(r'\n+', '\n', text)  # Replace multiple newlines with single newline
        # text = text.strip()  # Remove leading/trailing whitespace
        # return text
        
        return text.strip() if text else ""
    
    def _count_pages(self, file_path: str, content_type: str) -> int:
        """
        Count pages in document.
        
        TODO: Implement page counting for different file types:
        - PDF: Use PyPDF2 to count pages
        - DOCX: Count sections or estimate based on content
        - TXT: Return 1 (single page)
        
        Args:
            file_path: Path to the file
            content_type: MIME type of the file
            
        Returns:
            int: Number of pages
        """
        # TODO: Implement page counting
        return 1  # Placeholder
    
    def _count_words(self, text: str) -> int:
        """
        Count words in text.
        
        TODO: Implement word counting:
        - Split text on whitespace
        - Filter out empty strings
        - Return count
        
        Args:
            text: Text to count words in
            
        Returns:
            int: Number of words
        """
        # TODO: Implement word counting
        # HINT: Use text.split() and len()
        # HINT: Filter out empty strings
        
        return len(text.split()) if text else 0
