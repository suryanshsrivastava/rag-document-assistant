-- Migration: Alter embedding column in document_chunks to VECTOR(1536)
-- Ensures compatibility with Gemini embedding-001 (1536-dim)

ALTER TABLE document_chunks
  ALTER COLUMN embedding TYPE VECTOR(1536); 