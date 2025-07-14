-- Migration: Add missing sources column to chat_messages table
-- This fixes the schema mismatch where backend expects sources column

ALTER TABLE public.chat_messages 
ADD COLUMN IF NOT EXISTS sources JSONB DEFAULT '[]';

-- Add comment for documentation
COMMENT ON COLUMN public.chat_messages.sources IS 'JSON array containing source documents for RAG responses';
