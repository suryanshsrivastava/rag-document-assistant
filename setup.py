#!/usr/bin/env python3
"""
RAG System Setup Script

This script helps users set up the RAG system by:
1. Checking prerequisites
2. Creating environment files
3. Installing dependencies
4. Running initial tests
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")
    return True

def check_node_version():
    """Check if Node.js is installed."""
    try:
        result = subprocess.run(["node", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ Node.js {version} detected")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 18+")
        return False

def check_npm():
    """Check if npm is available."""
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.strip()
            print(f"✅ npm {version} detected")
            return True
        else:
            print("❌ npm not found")
            return False
    except FileNotFoundError:
        print("❌ npm not found")
        return False

def create_backend_env():
    """Create backend .env file if it doesn't exist."""
    env_path = Path("backend/.env")
    
    if env_path.exists():
        print("✅ Backend .env file already exists")
        return True
    
    print("📝 Creating backend .env file...")
    
    env_content = """# Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# Google Gemini Configuration
GEMINI_API_KEY=your_gemini_api_key

# Optional: Logging Level
LOG_LEVEL=INFO
"""
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Backend .env file created")
        print("   Please edit backend/.env with your actual credentials")
        return True
    except Exception as e:
        print(f"❌ Failed to create backend .env file: {e}")
        return False

def create_frontend_env():
    """Create frontend .env.local file if it doesn't exist."""
    env_path = Path("frontend/.env.local")
    
    if env_path.exists():
        print("✅ Frontend .env.local file already exists")
        return True
    
    print("📝 Creating frontend .env.local file...")
    
    env_content = """# Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000
"""
    
    try:
        with open(env_path, "w") as f:
            f.write(env_content)
        print("✅ Frontend .env.local file created")
        return True
    except Exception as e:
        print(f"❌ Failed to create frontend .env.local file: {e}")
        return False

def install_backend_dependencies():
    """Install backend Python dependencies."""
    print("📦 Installing backend dependencies...")
    
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "backend/requirements.txt"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Backend dependencies installed")
            return True
        else:
            print(f"❌ Failed to install backend dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install frontend Node.js dependencies."""
    print("📦 Installing frontend dependencies...")
    
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd="frontend",
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Frontend dependencies installed")
            return True
        else:
            print(f"❌ Failed to install frontend dependencies: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error installing frontend dependencies: {e}")
        return False

def run_backend_tests():
    """Run backend tests to verify setup."""
    print("🧪 Running backend tests...")
    
    try:
        result = subprocess.run(
            [sys.executable, "backend/test_backend.py"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Backend tests passed")
            return True
        else:
            print("⚠️  Backend tests failed. This is normal if credentials are not configured yet.")
            print("   Please configure your .env file and run tests again.")
            return True  # Don't fail setup for missing credentials
    except Exception as e:
        print(f"❌ Error running backend tests: {e}")
        return False

def create_database_schema():
    """Create database schema SQL file."""
    print("🗄️  Creating database schema...")
    
    schema_content = """-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    content_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    page_count INTEGER,
    word_count INTEGER,
    status TEXT DEFAULT 'processing',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Document chunks table
CREATE TABLE document_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    embedding VECTOR(1536),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create vector index
CREATE INDEX ON document_chunks USING ivfflat (embedding vector_cosine_ops);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chat messages table
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
"""
    
    try:
        with open("database_schema.sql", "w") as f:
            f.write(schema_content)
        print("✅ Database schema file created (database_schema.sql)")
        print("   Run this SQL in your Supabase SQL editor")
        return True
    except Exception as e:
        print(f"❌ Failed to create database schema: {e}")
        return False

def print_next_steps():
    """Print next steps for the user."""
    print("\n" + "=" * 60)
    print("🚀 Setup Complete! Next Steps:")
    print("=" * 60)
    
    print("\n1. Configure Environment Variables:")
    print("   - Edit backend/.env with your Supabase and Gemini credentials")
    print("   - Get Supabase credentials from your Supabase project dashboard")
    print("   - Get Gemini API key from Google AI Studio")
    
    print("\n2. Set Up Database:")
    print("   - Go to your Supabase project SQL editor")
    print("   - Run the SQL from database_schema.sql")
    print("   - Enable the pgvector extension")
    
    print("\n3. Start the Application:")
    print("   Terminal 1 (Backend):")
    print("   cd backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000")
    print("   ")
    print("   Terminal 2 (Frontend):")
    print("   cd frontend && npm run dev")
    
    print("\n4. Test the System:")
    print("   - Backend: http://localhost:8000")
    print("   - Frontend: http://localhost:3000")
    print("   - API Docs: http://localhost:8000/docs")
    
    print("\n5. Run End-to-End Tests:")
    print("   python test_e2e.py")
    
    print("\n📚 For more information, see README.md")

def main():
    """Main setup function."""
    print("🔧 RAG System Setup")
    print("=" * 60)
    
    # Check prerequisites
    print("\n📋 Checking Prerequisites...")
    if not check_python_version():
        return False
    
    if not check_node_version():
        print("   Please install Node.js 18+ and try again")
        return False
    
    if not check_npm():
        print("   Please install npm and try again")
        return False
    
    # Create environment files
    print("\n📝 Creating Environment Files...")
    if not create_backend_env():
        return False
    
    if not create_frontend_env():
        return False
    
    # Install dependencies
    print("\n📦 Installing Dependencies...")
    if not install_backend_dependencies():
        return False
    
    if not install_frontend_dependencies():
        return False
    
    # Create database schema
    print("\n🗄️  Setting Up Database...")
    if not create_database_schema():
        return False
    
    # Run tests
    print("\n🧪 Running Tests...")
    run_backend_tests()
    
    # Print next steps
    print_next_steps()
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 