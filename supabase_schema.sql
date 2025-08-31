-- Supabase Database Schema for Intelligent Document Workspace
-- This schema supports RAG capabilities, conversation management, and user data
-- Run these commands in your Supabase SQL editor

-- Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "vector"; -- pgvector for embeddings

-- Users table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    display_name TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- User preferences and settings
    settings JSONB DEFAULT '{}'::jsonb
);

-- Documents table - stores uploaded document metadata
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    original_filename TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    content_type TEXT NOT NULL,
    
    -- Document processing status
    processing_status TEXT NOT NULL DEFAULT 'processing' 
        CHECK (processing_status IN ('processing', 'completed', 'failed')),
    
    -- Extracted content and metadata
    content TEXT, -- Full text content extracted from document
    chunk_count INTEGER DEFAULT 0,
    word_count INTEGER DEFAULT 0,
    
    -- File storage information
    storage_path TEXT, -- Path in Supabase storage
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processed_at TIMESTAMP WITH TIME ZONE,
    
    -- Metadata extracted from document
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Document chunks table - stores text chunks with embeddings for RAG
CREATE TABLE IF NOT EXISTS public.document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
    
    -- Chunk information
    chunk_index INTEGER NOT NULL, -- Order within the document
    content TEXT NOT NULL, -- The actual text chunk
    word_count INTEGER NOT NULL DEFAULT 0,
    
    -- Vector embedding for semantic search
    embedding vector(768), -- Google Gemini embedding-001 dimension
    
    -- Chunk metadata
    page_number INTEGER, -- For PDFs
    section_title TEXT, -- If we can extract section headers
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Composite index for efficient queries
    UNIQUE(document_id, chunk_index)
);

-- Conversations table - manages chat sessions
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    
    -- Conversation metadata
    title TEXT, -- Auto-generated or user-provided title
    summary TEXT, -- AI-generated summary of conversation
    
    -- Associated documents for this conversation
    document_ids UUID[] DEFAULT '{}', -- Array of document IDs
    
    -- Conversation state
    status TEXT NOT NULL DEFAULT 'active' 
        CHECK (status IN ('active', 'archived', 'deleted')),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Conversation metadata
    metadata JSONB DEFAULT '{}'::jsonb
);

-- Messages table - stores individual chat messages
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    
    -- Message metadata
    token_count INTEGER, -- For tracking API usage
    processing_time_ms INTEGER, -- Response time tracking
    
    -- Sources used in AI response (for assistant messages)
    sources JSONB DEFAULT '[]'::jsonb, -- Array of source information
    
    -- Message context
    context_used JSONB DEFAULT '{}'::jsonb, -- Retrieved chunks used for this response
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Ordering within conversation
    message_order INTEGER NOT NULL DEFAULT 0
);

-- Create indexes for optimal query performance
-- These indexes are crucial for RAG performance and chat functionality

-- Vector similarity search index (most important for RAG)
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding_cosine 
    ON public.document_chunks USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- Document queries
CREATE INDEX IF NOT EXISTS idx_documents_user_id 
    ON public.documents(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_documents_status 
    ON public.documents(processing_status, created_at DESC);

-- Chunk queries
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id 
    ON public.document_chunks(document_id, chunk_index);

-- Conversation queries
CREATE INDEX IF NOT EXISTS idx_conversations_user_id 
    ON public.conversations(user_id, last_message_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversations_status 
    ON public.conversations(status, last_message_at DESC);

-- Message queries
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id 
    ON public.messages(conversation_id, message_order);

CREATE INDEX IF NOT EXISTS idx_messages_created_at 
    ON public.messages(created_at DESC);

-- Row Level Security (RLS) policies for data protection
-- These ensure users can only access their own data

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;

-- Users can only access their own data
CREATE POLICY "Users can access own data" ON public.users
    FOR ALL USING (auth.uid() = id);

-- Documents access policies
CREATE POLICY "Users can access own documents" ON public.documents
    FOR ALL USING (auth.uid() = user_id);

-- Document chunks inherit permissions from documents
CREATE POLICY "Users can access chunks of own documents" ON public.document_chunks
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.documents 
            WHERE documents.id = document_chunks.document_id 
            AND documents.user_id = auth.uid()
        )
    );

-- Conversations access policies
CREATE POLICY "Users can access own conversations" ON public.conversations
    FOR ALL USING (auth.uid() = user_id);

-- Messages inherit permissions from conversations
CREATE POLICY "Users can access messages in own conversations" ON public.messages
    FOR ALL USING (
        EXISTS (
            SELECT 1 FROM public.conversations 
            WHERE conversations.id = messages.conversation_id 
            AND conversations.user_id = auth.uid()
        )
    );

-- Useful functions for the application

-- Function to update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply the update trigger to relevant tables
CREATE TRIGGER update_documents_updated_at 
    BEFORE UPDATE ON public.documents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at 
    BEFORE UPDATE ON public.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to automatically update conversation's last_message_at
CREATE OR REPLACE FUNCTION update_conversation_last_message()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.conversations 
    SET last_message_at = NOW(), updated_at = NOW()
    WHERE id = NEW.conversation_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_conversation_on_message 
    AFTER INSERT ON public.messages
    FOR EACH ROW EXECUTE FUNCTION update_conversation_last_message();

-- Function to count chunks and update document
CREATE OR REPLACE FUNCTION update_document_chunk_count()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.documents 
    SET chunk_count = (
        SELECT COUNT(*) 
        FROM public.document_chunks 
        WHERE document_id = NEW.document_id
    )
    WHERE id = NEW.document_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_chunk_count_on_insert 
    AFTER INSERT ON public.document_chunks
    FOR EACH ROW EXECUTE FUNCTION update_document_chunk_count();

-- Vector similarity search function
-- This is the core function that powers your RAG system
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 10,
    filter_document_ids uuid[] DEFAULT NULL
)
RETURNS TABLE (
    chunk_id uuid,
    document_id uuid,
    content text,
    similarity float,
    chunk_index int,
    document_filename text
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id as chunk_id,
        dc.document_id,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity,
        dc.chunk_index,
        d.filename as document_filename
    FROM public.document_chunks dc
    JOIN public.documents d ON dc.document_id = d.id
    WHERE 
        dc.embedding <=> query_embedding < 1 - match_threshold
        AND (filter_document_ids IS NULL OR d.id = ANY(filter_document_ids))
        AND d.processing_status = 'completed'
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Sample data for testing (optional - remove in production)
-- This helps you test the system quickly during development

-- INSERT INTO public.users (id, email, display_name) VALUES
-- ('550e8400-e29b-41d4-a716-446655440000', 'demo@example.com', 'Demo User')
-- ON CONFLICT (id) DO NOTHING;

-- Helpful queries for development and debugging

-- Check vector extension is working
-- SELECT * FROM pg_extension WHERE extname = 'vector';

-- View document processing status
-- SELECT filename, processing_status, chunk_count, created_at 
-- FROM public.documents ORDER BY created_at DESC;

-- Check embedding generation progress
-- SELECT d.filename, COUNT(dc.id) as chunks_with_embeddings
-- FROM public.documents d
-- LEFT JOIN public.document_chunks dc ON d.id = dc.document_id 
-- WHERE dc.embedding IS NOT NULL
-- GROUP BY d.id, d.filename;

-- Test similarity search (replace with actual embedding)
-- SELECT * FROM search_similar_chunks(
--     '[0.1, 0.2, 0.3, ...]'::vector(1536),
--     0.7,
--     5
-- );