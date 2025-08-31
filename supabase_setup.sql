-- Weekend RAG System - Supabase Database Setup
-- This script sets up the necessary tables and functions for the RAG system

-- Enable the pgvector extension for vector operations
CREATE EXTENSION IF NOT EXISTS vector;

-- Create documents table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    content TEXT NOT NULL,
    chunk_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    processing_status TEXT DEFAULT 'pending'
);

-- Create document_chunks table with vector storage
CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    embedding vector(768), -- Google Gemini embedding-001 dimension
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(document_id, chunk_index)
);

-- Create conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_message TEXT NOT NULL,
    assistant_response TEXT NOT NULL,
    sources JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_document_chunks_document_id ON document_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_document_chunks_embedding ON document_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX IF NOT EXISTS idx_conversations_created_at ON conversations(created_at);

-- Function to search for similar chunks using vector similarity
CREATE OR REPLACE FUNCTION search_similar_chunks(
    query_embedding vector(1536),
    match_threshold float DEFAULT 0.7,
    match_count int DEFAULT 5
)
RETURNS TABLE (
    id UUID,
    document_id UUID,
    chunk_index INTEGER,
    content TEXT,
    similarity float,
    document_filename TEXT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dc.id,
        dc.document_id,
        dc.chunk_index,
        dc.content,
        1 - (dc.embedding <=> query_embedding) as similarity,
        d.filename as document_filename
    FROM document_chunks dc
    JOIN documents d ON dc.document_id = d.id
    WHERE 1 - (dc.embedding <=> query_embedding) > match_threshold
    ORDER BY dc.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to update document chunk count
CREATE OR REPLACE FUNCTION update_document_chunk_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE documents 
        SET chunk_count = chunk_count + 1,
            updated_at = NOW()
        WHERE id = NEW.document_id;
        RETURN NEW;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE documents 
        SET chunk_count = chunk_count - 1,
            updated_at = NOW()
        WHERE id = OLD.document_id;
        RETURN OLD;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update chunk count
CREATE TRIGGER update_chunk_count_trigger
    AFTER INSERT OR DELETE ON document_chunks
    FOR EACH ROW
    EXECUTE FUNCTION update_document_chunk_count();

-- Enable Row Level Security (RLS)
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

-- Create policies for public access (for demo purposes)
-- In production, you would want proper authentication
CREATE POLICY "Allow public read access to documents" ON documents
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to documents" ON documents
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to document_chunks" ON document_chunks
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to document_chunks" ON document_chunks
    FOR INSERT WITH CHECK (true);

CREATE POLICY "Allow public read access to conversations" ON conversations
    FOR SELECT USING (true);

CREATE POLICY "Allow public insert access to conversations" ON conversations
    FOR INSERT WITH CHECK (true);

-- Insert some sample data for testing
INSERT INTO documents (id, filename, content, chunk_count, processing_status) VALUES
    ('550e8400-e29b-41d4-a716-446655440000', 'sample_document.txt', 'This is a sample document for testing the RAG system. It contains information about artificial intelligence and machine learning.', 1, 'completed')
ON CONFLICT (id) DO NOTHING;

-- Sample conversation
INSERT INTO conversations (id, user_message, assistant_response, sources) VALUES
    ('550e8400-e29b-41d4-a716-446655440001', 'What is AI?', 'Based on the uploaded documents, AI refers to artificial intelligence which includes machine learning technologies.', '[]')
ON CONFLICT (id) DO NOTHING; 