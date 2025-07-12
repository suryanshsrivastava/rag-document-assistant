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
        
        TODO: Implement the complete document processing workflow:
        
        1. VALIDATE FILE
           - Check file type against allowed_types
           - Validate file size
           - Check file extension
        
        2. SAVE FILE
           - Generate unique filename
           - Save to upload directory
           - Return file path
        
        3. EXTRACT TEXT
           - Handle different file types
           - Clean extracted text
           - Handle extraction errors
        
        4. EXTRACT METADATA
           - Get file info (size, type, etc.)
           - Extract document-specific metadata
           - Count pages/words
        
        5. RETURN STRUCTURED DATA
           - Return dictionary with all extracted information
        
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
            # TODO: Step 1 - Validate the file
            # HINT: Call self._validate_file(file)
            # HINT: Raise HTTPException with status_code=400 if validation fails
            
            # TODO: Step 2 - Save the file
            # HINT: Call self._save_file(file)
            # HINT: Store the returned file_path
            
            # TODO: Step 3 - Extract text content
            # HINT: Call self._extract_text(file_path, file.content_type)
            # HINT: Handle cases where text extraction fails
            
            # TODO: Step 4 - Extract metadata
            # HINT: Call self._extract_metadata(file_path, file.content_type)
            # HINT: Include file size, creation date, etc.
            
            # TODO: Step 5 - Return structured result
            # HINT: Return a dictionary with all the extracted information
            # HINT: Generate a unique file_id using str(uuid.uuid4())
            
            # PLACEHOLDER RETURN (replace with actual implementation)
            return {
                "file_id": str(uuid.uuid4()),
                "filename": file.filename,
                "file_path": "temp_path",
                "text_content": "TODO: Extract actual text content",
                "metadata": {
                    "file_size": 0,
                    "page_count": 0,
                    "word_count": 0,
                    "content_type": file.content_type
                },
                "status": "processed"
            }
            
        except Exception as e:
            logger.error(f"Error processing document {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")
    
    def _validate_file(self, file: UploadFile) -> bool:
        """
        Validate uploaded file type and size.
        
        TODO: Implement file validation logic:
        
        1. CHECK FILE TYPE
           - Verify file.content_type is in self.allowed_types
           - Get file extension from filename
           - Ensure extension matches content type
        
        2. CHECK FILE SIZE
           - Ensure file size is within limits
           - Handle cases where file.size might be None
        
        3. CHECK FILE INTEGRITY
           - Ensure file is not corrupted
           - Check if file has content
        
        Args:
            file: FastAPI UploadFile object
            
        Returns:
            bool: True if file is valid, False otherwise
            
        Raises:
            HTTPException: If file validation fails
        """
        # TODO: Implement file validation
        # HINT: Check if file.content_type in self.allowed_types
        # HINT: Use file.filename.lower().endswith() to check extensions
        # HINT: Compare file size with self.max_file_size
        
        # Example validation structure:
        # if file.content_type not in self.allowed_types:
        #     raise HTTPException(400, "Unsupported file type")
        # 
        # if file.size > self.max_file_size:
        #     raise HTTPException(400, "File too large")
        
        return True  # TODO: Replace with actual validation
    
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
        # TODO: Implement file saving
        # HINT: Generate unique filename with uuid.uuid4()
        # HINT: Keep original file extension
        # HINT: Use file.read() to get file content
        # HINT: Use open() with 'wb' mode to write binary data
        
        # Example structure:
        # file_id = str(uuid.uuid4())
        # file_extension = os.path.splitext(file.filename)[1]
        # unique_filename = f"{file_id}{file_extension}"
        # file_path = os.path.join(self.upload_dir, unique_filename)
        # 
        # with open(file_path, "wb") as f:
        #     content = await file.read()
        #     f.write(content)
        # 
        # return file_path
        
        return "TODO: Implement file saving"
    
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
        # TODO: Implement text extraction for different file types
        
        if content_type == "application/pdf":
            # TODO: Extract text from PDF
            # HINT: Use PyPDF2.PdfReader(file_path)
            # HINT: Iterate through pages and extract text
            # HINT: Handle exceptions for corrupted PDFs
            
            # Example structure:
            # with open(file_path, 'rb') as file:
            #     pdf_reader = PyPDF2.PdfReader(file)
            #     text = ""
            #     for page in pdf_reader.pages:
            #         text += page.extract_text()
            #     return self._clean_text(text)
            
            return "TODO: Extract PDF text"
        
        elif content_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            # TODO: Extract text from DOCX
            # HINT: Use docx.Document(file_path)
            # HINT: Iterate through paragraphs
            # HINT: Extract text from tables if needed
            
            # Example structure:
            # doc = docx.Document(file_path)
            # text = ""
            # for paragraph in doc.paragraphs:
            #     text += paragraph.text + "\n"
            # return self._clean_text(text)
            
            return "TODO: Extract DOCX text"
        
        elif content_type == "text/plain":
            # TODO: Extract text from plain text file
            # HINT: Use open() with appropriate encoding
            # HINT: Handle different encodings (utf-8, latin-1, etc.)
            
            # Example structure:
            # with open(file_path, 'r', encoding='utf-8') as file:
            #     text = file.read()
            #     return self._clean_text(text)
            
            return "TODO: Extract plain text"
        
        else:
            raise Exception(f"Unsupported file type: {content_type}")
    
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
        # TODO: Implement metadata extraction
        # HINT: Use os.path.getsize() for file size
        # HINT: Use os.path.getmtime() for modification time
        # HINT: Count words by splitting text on whitespace
        
        # Example structure:
        # metadata = {
        #     "file_size": os.path.getsize(file_path),
        #     "content_type": content_type,
        #     "page_count": self._count_pages(file_path, content_type),
        #     "word_count": self._count_words(text_content),
        #     "character_count": len(text_content),
        #     "created_at": datetime.now().isoformat()
        # }
        
        return {
            "file_size": 0,
            "page_count": 0,
            "word_count": 0,
            "character_count": 0,
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
