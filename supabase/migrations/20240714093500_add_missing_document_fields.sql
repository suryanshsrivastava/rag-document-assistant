-- Migration: Add missing fields to documents table for backend model compatibility
-- This fixes the schema drift between backend models and database

-- Add page_count column
ALTER TABLE public.documents
ADD COLUMN page_count INTEGER DEFAULT NULL;

-- Add word_count column  
ALTER TABLE public.documents
ADD COLUMN word_count INTEGER DEFAULT NULL;

-- Add status column
ALTER TABLE public.documents
ADD COLUMN status TEXT NOT NULL DEFAULT 'processing';

-- Add comment to clarify the difference between file_type and content_type
COMMENT ON COLUMN public.documents.file_type IS 'Original file extension/type';
COMMENT ON COLUMN public.documents.content_type IS 'MIME type for HTTP content-type header';
