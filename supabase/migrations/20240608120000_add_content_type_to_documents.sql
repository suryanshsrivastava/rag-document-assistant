-- Migration: Add content_type column to public.documents
ALTER TABLE public.documents
ADD COLUMN content_type TEXT NOT NULL DEFAULT 'application/octet-stream'; 