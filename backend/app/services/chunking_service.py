"""
Text Chunking Service for RAG System

Handles intelligent text chunking with overlap for optimal embedding generation.
"""

import re
from typing import List, Dict, Any, Optional
import logging
from .constants import CHUNK_SIZE, CHUNK_OVERLAP

logger = logging.getLogger(__name__)

class ChunkingService:
    """Service for chunking text documents with intelligent splitting."""
    
    def __init__(self, chunk_size: int = CHUNK_SIZE, overlap_size: int = CHUNK_OVERLAP):
        """
        Initialize the chunking service.
        
        Args:
            chunk_size: Target size for each chunk in characters
            overlap_size: Overlap between consecutive chunks in characters
        """
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size
    
    def chunk_text(self, text: str, document_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text content to chunk
            document_id: Optional document ID for reference
            
        Returns:
            List of chunk dictionaries with text and metadata
        """
        try:
            # Clean and normalize text
            cleaned_text = self._clean_text(text)
            
            # Split into sentences first
            sentences = self._split_into_sentences(cleaned_text)
            
            # Create chunks with overlap
            chunks = self._create_chunks_with_overlap(sentences)
            
            # Add metadata to chunks
            chunked_data = []
            for i, chunk in enumerate(chunks):
                chunk_data = {
                    "chunk_id": f"{document_id}_chunk_{i}" if document_id else f"chunk_{i}",
                    "chunk_text": chunk,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "metadata": {
                        "document_id": document_id,
                        "chunk_number": i + 1,
                        "total_chunks": len(chunks)
                    }
                }
                chunked_data.append(chunk_data)
            
            logger.info(f"Created {len(chunked_data)} chunks from text")
            return chunked_data
            
        except Exception as e:
            logger.error(f"Error chunking text: {str(e)}")
            raise Exception(f"Text chunking failed: {str(e)}")
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text for chunking.
        
        Args:
            text: Raw text content
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might interfere with chunking
        text = re.sub(r'[\r\n\t]+', ' ', text)
        
        # Normalize quotes and dashes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace('–', '-').replace('—', '-')
        
        return text.strip()
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """
        Split text into sentences using intelligent boundaries.
        
        Args:
            text: Clean text content
            
        Returns:
            List of sentences
        """
        # Split on sentence boundaries (period, exclamation, question mark)
        # but preserve abbreviations and common patterns
        sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
        sentences = re.split(sentence_pattern, text)
        
        # Filter out empty sentences
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _create_chunks_with_overlap(self, sentences: List[str]) -> List[str]:
        """
        Create chunks with overlap from sentences.
        
        Args:
            sentences: List of sentences
            
        Returns:
            List of text chunks
        """
        chunks = []
        current_chunk = ""
        sentence_index = 0
        
        while sentence_index < len(sentences):
            sentence = sentences[sentence_index]
            
            # If adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) + 1 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    
                    # Start new chunk with overlap
                    overlap_start = max(0, len(current_chunk) - self.overlap_size)
                    overlap_text = current_chunk[overlap_start:]
                    current_chunk = overlap_text + " " + sentence
                else:
                    # Single sentence is too long, split it
                    if len(sentence) > self.chunk_size:
                        # Split long sentence into smaller pieces
                        sub_chunks = self._split_long_sentence(sentence)
                        chunks.extend(sub_chunks)
                        current_chunk = ""
                    else:
                        current_chunk = sentence
            else:
                # Add sentence to current chunk
                if current_chunk:
                    current_chunk += " " + sentence
                else:
                    current_chunk = sentence
            
            sentence_index += 1
        
        # Add the last chunk if it exists
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _split_long_sentence(self, sentence: str) -> List[str]:
        """
        Split a very long sentence into smaller chunks.
        
        Args:
            sentence: Long sentence to split
            
        Returns:
            List of smaller text chunks
        """
        words = sentence.split()
        chunks = []
        current_chunk = ""
        
        for word in words:
            if len(current_chunk) + len(word) + 1 > self.chunk_size:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                    current_chunk = word
                else:
                    # Single word is too long, truncate
                    chunks.append(word[:self.chunk_size])
            else:
                if current_chunk:
                    current_chunk += " " + word
                else:
                    current_chunk = word
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def get_chunk_statistics(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get statistics about the chunking process.
        
        Args:
            chunks: List of chunk dictionaries
            
        Returns:
            Dictionary with chunking statistics
        """
        if not chunks:
            return {
                "total_chunks": 0,
                "average_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
                "total_characters": 0
            }
        
        chunk_sizes = [len(chunk["chunk_text"]) for chunk in chunks]
        total_chars = sum(chunk_sizes)
        
        return {
            "total_chunks": len(chunks),
            "average_chunk_size": total_chars / len(chunks),
            "min_chunk_size": min(chunk_sizes),
            "max_chunk_size": max(chunk_sizes),
            "total_characters": total_chars
        } 