"""
Gemini Client Service for RAG System

Handles Google Gemini API interactions for embeddings and chat completions.
"""

import os
import asyncio
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class GeminiClient:
    """Service for Google Gemini API interactions."""
    
    def __init__(self):
        """Initialize Gemini client with API key."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Initialize models
        self.embedding_model = "models/embedding-001"  # Gemini embedding model
        self.chat_model = "gemini-1.5-flash"  # Use stable model
        
        logger.info("Gemini client initialized successfully")
    
    async def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            embeddings = []
            
            # Process in batches to handle rate limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                # Generate embeddings using Gemini
                batch_embeddings = []
                
                for text in batch:
                    # Use the correct API call for embedding generation
                    result = genai.embed_content(
                        model=self.embedding_model,
                        content=text
                    )
                    batch_embeddings.append(result['embedding'])
                
                embeddings.extend(batch_embeddings)
                
                # Add delay between batches to respect rate limits
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise Exception(f"Embedding generation failed: {str(e)}")
    
    async def generate_chat_completion(
        self, 
        messages: List[Dict[str, str]], 
        context: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """
        Generate chat completion with optional context.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            context: Optional context to prepend to the conversation
            temperature: Sampling temperature for response generation
            
        Returns:
            Generated response text
        """
        try:
            # Initialize Gemini model
            model = genai.GenerativeModel(self.chat_model)
            
            # Prepare conversation history
            conversation = model.start_chat(history=[])
            
            # Add context if provided
            if context:
                system_message = f"You are a helpful AI assistant. Use the following context to answer questions: {context}"
                # Add system message to conversation
                conversation.send_message(system_message)
            
            # Add user messages
            for message in messages:
                if message["role"] == "user":
                    response = conversation.send_message(message["content"])
                    return response.text
            
            # If no user message found, use the last message
            if messages:
                last_message = messages[-1]["content"]
                response = conversation.send_message(last_message)
                return response.text
            
            return "No message provided"
            
        except Exception as e:
            logger.error(f"Error generating chat completion: {str(e)}")
            raise Exception(f"Chat completion failed: {str(e)}")
    
    async def generate_rag_response(
        self, 
        user_message: str, 
        context_chunks: List[Dict[str, Any]],
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Generate RAG response using retrieved context.
        
        Args:
            user_message: User's question or message
            context_chunks: List of relevant document chunks
            conversation_history: Optional conversation history
            
        Returns:
            Generated response with context
        """
        try:
            # Prepare context from chunks
            context_text = self._prepare_context_from_chunks(context_chunks)
            
            # Prepare messages
            messages = []
            
            if conversation_history:
                messages.extend(conversation_history)
            
            messages.append({
                "role": "user",
                "content": user_message
            })
            
            # Generate response with context
            response = await self.generate_chat_completion(
                messages=messages,
                context=context_text,
                temperature=0.7
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            raise Exception(f"RAG response generation failed: {str(e)}")
    
    def _prepare_context_from_chunks(self, chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from document chunks.
        
        Args:
            chunks: List of document chunks with text and metadata
            
        Returns:
            Formatted context string
        """
        if not chunks:
            return ""
        
        context_parts = []
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.get("chunk_text", "")
            document_id = chunk.get("metadata", {}).get("document_id", "Unknown")
            
            context_part = f"Document {document_id}, Chunk {i+1}:\n{chunk_text}\n"
            context_parts.append(context_part)
        
        return "\n".join(context_parts)
    
    async def test_connection(self) -> bool:
        """
        Test Gemini API connection.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Simple test with a short text
            test_embeddings = await self.generate_embeddings(["test"])
            return len(test_embeddings) > 0
        except Exception as e:
            logger.error(f"Gemini connection test failed: {str(e)}")
            return False 