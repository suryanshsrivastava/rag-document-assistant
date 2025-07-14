-- Migration: Add anonymous access policies for testing
-- This allows the RAG system to work without full authentication
-- WARNING: These policies are for development/testing only

-- Add anonymous access policy for documents table
CREATE POLICY "Allow anonymous access to documents" ON public.documents
    FOR ALL USING (true)
    WITH CHECK (true);

-- Add anonymous access policy for document_chunks table  
CREATE POLICY "Allow anonymous access to document_chunks" ON public.document_chunks
    FOR ALL USING (true)
    WITH CHECK (true);

-- Add anonymous access policy for chat_messages table
CREATE POLICY "Allow anonymous access to chat_messages" ON public.chat_messages
    FOR ALL USING (true)
    WITH CHECK (true);

-- Add anonymous access policy for users table (for testing)
CREATE POLICY "Allow anonymous access to users" ON public.users
    FOR ALL USING (true)
    WITH CHECK (true);

-- Comment explaining these are for development
COMMENT ON POLICY "Allow anonymous access to documents" ON public.documents IS 'Development/testing policy - allows anonymous access to documents';
COMMENT ON POLICY "Allow anonymous access to document_chunks" ON public.document_chunks IS 'Development/testing policy - allows anonymous access to document chunks';
COMMENT ON POLICY "Allow anonymous access to chat_messages" ON public.chat_messages IS 'Development/testing policy - allows anonymous access to chat messages';
COMMENT ON POLICY "Allow anonymous access to users" ON public.users IS 'Development/testing policy - allows anonymous access to users';
