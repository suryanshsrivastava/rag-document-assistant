-- Migration: Add conversation_id column to chat_messages
ALTER TABLE public.chat_messages
ADD COLUMN conversation_id UUID; 