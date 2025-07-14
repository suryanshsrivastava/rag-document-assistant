-- Migration: Add filename column to public.documents
ALTER TABLE public.documents
ADD COLUMN filename TEXT NOT NULL DEFAULT 'untitled'; 