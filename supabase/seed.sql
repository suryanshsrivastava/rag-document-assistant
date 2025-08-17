-- Seed data for Weekend RAG System
-- This file will be executed after migrations during db reset

-- Insert sample users (these would normally be created through Supabase Auth)
INSERT INTO public.users (id, username, email) VALUES
('550e8400-e29b-41d4-a716-446655440000', 'demo_user', 'demo@example.com'),
('550e8400-e29b-41d4-a716-446655440001', 'test_user', 'test@example.com')
ON CONFLICT (id) DO NOTHING;

-- Insert sample habits
INSERT INTO public.habits (id, user_id, name, description, frequency) VALUES
('550e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440000', 'Morning Exercise', 'Do 30 minutes of exercise every morning', 'daily'),
('550e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440000', 'Read Books', 'Read at least 30 pages of a book', 'daily'),
('550e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440000', 'Meditation', 'Practice mindfulness meditation', 'daily'),
('550e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440001', 'Weekly Planning', 'Plan the upcoming week', 'weekly')
ON CONFLICT (id) DO NOTHING;

-- Insert sample habit logs
INSERT INTO public.habit_logs (id, habit_id, completed_at, notes) VALUES
('550e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '1 day', 'Great workout today!'),
('550e8400-e29b-41d4-a716-446655440007', '550e8400-e29b-41d4-a716-446655440002', NOW() - INTERVAL '2 days', 'Felt energized'),
('550e8400-e29b-41d4-a716-446655440008', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '1 day', 'Read about AI and machine learning'),
('550e8400-e29b-41d4-a716-446655440009', '550e8400-e29b-41d4-a716-446655440003', NOW() - INTERVAL '2 days', 'Finished chapter 5'),
('550e8400-e29b-41d4-a716-446655440010', '550e8400-e29b-41d4-a716-446655440004', NOW() - INTERVAL '3 days', 'Focused on breathing exercises'),
('550e8400-e29b-41d4-a716-446655440011', '550e8400-e29b-41d4-a716-446655440005', NOW() - INTERVAL '7 days', 'Planned next week goals')
ON CONFLICT (id) DO NOTHING;

-- Insert sample streaks
INSERT INTO public.streaks (id, habit_id, current_streak, longest_streak, last_completed) VALUES
('550e8400-e29b-41d4-a716-446655440012', '550e8400-e29b-41d4-a716-446655440002', 5, 10, CURRENT_DATE - INTERVAL '1 day'),
('550e8400-e29b-41d4-a716-446655440013', '550e8400-e29b-41d4-a716-446655440003', 3, 7, CURRENT_DATE - INTERVAL '1 day'),
('550e8400-e29b-41d4-a716-446655440014', '550e8400-e29b-41d4-a716-446655440004', 0, 5, CURRENT_DATE - INTERVAL '3 days'),
('550e8400-e29b-41d4-a716-446655440015', '550e8400-e29b-41d4-a716-446655440005', 1, 3, CURRENT_DATE - INTERVAL '7 days')
ON CONFLICT (id) DO NOTHING;

-- Insert sample documents for RAG system
INSERT INTO public.documents (id, user_id, title, content, file_path, file_type, file_size) VALUES
('550e8400-e29b-41d4-a716-446655440016', '550e8400-e29b-41d4-a716-446655440000', 'AI and Machine Learning Guide', 'This is a comprehensive guide to artificial intelligence and machine learning concepts. It covers topics like neural networks, deep learning, and natural language processing.', '/documents/ai_guide.txt', 'text/plain', 2048),
('550e8400-e29b-41d4-a716-446655440017', '550e8400-e29b-41d4-a716-446655440000', 'Productivity Tips', 'A collection of productivity tips and techniques for better time management and work efficiency.', '/documents/productivity_tips.txt', 'text/plain', 1024),
('550e8400-e29b-41d4-a716-446655440018', '550e8400-e29b-41d4-a716-446655440001', 'Programming Best Practices', 'Guidelines and best practices for writing clean, maintainable code in various programming languages.', '/documents/programming_best_practices.txt', 'text/plain', 3072)
ON CONFLICT (id) DO NOTHING;

-- Insert sample chat messages
INSERT INTO public.chat_messages (id, user_id, session_id, role, content, metadata) VALUES
('550e8400-e29b-41d4-a716-446655440019', '550e8400-e29b-41d4-a716-446655440000', 'session_001', 'user', 'What are the best practices for machine learning?', '{"source": "web"}'),
('550e8400-e29b-41d4-a716-446655440020', '550e8400-e29b-41d4-a716-446655440000', 'session_001', 'assistant', 'Based on the AI guide in your documents, here are some key best practices for machine learning...', '{"model": "gpt-4", "tokens_used": 150}'),
('550e8400-e29b-41d4-a716-446655440021', '550e8400-e29b-41d4-a716-446655440001', 'session_002', 'user', 'How can I improve my productivity?', '{"source": "mobile"}'),
('550e8400-e29b-41d4-a716-446655440022', '550e8400-e29b-41d4-a716-446655440001', 'session_002', 'assistant', 'According to your productivity tips document, here are several techniques you can use...', '{"model": "gpt-4", "tokens_used": 200}')
ON CONFLICT (id) DO NOTHING; 