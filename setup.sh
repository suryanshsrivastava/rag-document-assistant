#!/bin/bash

# Weekend RAG System - Complete Setup Script
# This script sets up the entire RAG system with Next.js, FastAPI, and Supabase

set -e

echo "🚀 Setting up Weekend RAG System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    print_error "Please run this script from the project root directory"
    exit 1
fi

print_status "Setting up Python virtual environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
print_status "Installing Python dependencies..."
pip install -r requirements.txt
pip install PyPDF2 google-generativeai python-dotenv

print_success "Python dependencies installed"

# Install Node.js dependencies
print_status "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

print_success "Node.js dependencies installed"

# Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p backend/chroma_db

# Copy environment file if it doesn't exist
if [ ! -f "backend/.env" ]; then
    cp backend/.env.example backend/.env
    print_warning "Environment file created. Please update backend/.env with your API keys:"
    echo "  - SUPABASE_URL: Your Supabase project URL"
    echo "  - SUPABASE_ANON_KEY: Your Supabase anon key"
    echo "  - GOOGLE_API_KEY: Your Google API key for Gemini"
else
    print_status "Environment file already exists"
fi

# Create a simple test document
print_status "Creating test document..."
cat > test_document.txt << EOF
Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that work and react like humans.

Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.

Deep Learning is a subset of machine learning that uses neural networks with multiple layers to model and understand complex patterns.

Natural Language Processing (NLP) is a field of AI that focuses on the interaction between computers and human language.

Computer Vision is a field of AI that trains computers to interpret and understand visual information from the world.
EOF

print_success "Test document created: test_document.txt"

# Create startup script
print_status "Creating startup script..."
cat > start_servers.sh << 'EOF'
#!/bin/bash

# Weekend RAG System - Server Startup Script

echo "🚀 Starting Weekend RAG System..."

# Function to cleanup background processes
cleanup() {
    echo "🛑 Stopping servers..."
    pkill -f "uvicorn"
    pkill -f "next dev"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start backend server
echo "📡 Starting FastAPI backend..."
source venv/bin/activate
cd backend
python mvp_main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend server
echo "🌐 Starting Next.js frontend..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Servers started successfully!"
echo "📊 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID
EOF

chmod +x start_servers.sh

print_success "Startup script created: start_servers.sh"

# Create README with setup instructions
print_status "Creating comprehensive README..."
cat > README.md << 'EOF'
# Weekend RAG System

A complete Retrieval-Augmented Generation (RAG) system built with Next.js, FastAPI, and Supabase.

## 🚀 Features

- **Document Upload**: Upload PDF and TXT files
- **Vector Storage**: Store document embeddings in Supabase
- **AI Chat**: Chat with your documents using Google Gemini
- **Modern UI**: Beautiful, responsive interface
- **Real-time Processing**: Fast document processing and chunking

## 🛠️ Technology Stack

- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: Supabase with PostgreSQL and pgvector
- **AI**: Google Gemini models for embeddings and text generation
- **File Processing**: PyPDF2 for PDF extraction

## 📋 Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account
- Google API key for Gemini

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone <your-repo-url>
cd weekend-rag-system
chmod +x setup.sh
./setup.sh
```

### 2. Configure Environment Variables

Edit `backend/.env` with your API keys:

```env
SUPABASE_URL=your_supabase_url_here
SUPABASE_ANON_KEY=your_supabase_anon_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### 3. Set up Supabase Database

1. Create a new Supabase project
2. Run the SQL script in `supabase_setup.sql` in your Supabase SQL editor
3. Copy your project URL and anon key to the `.env` file

### 4. Start the Servers

```bash
./start_servers.sh
```

Or start them manually:

```bash
# Terminal 1 - Backend
source venv/bin/activate
cd backend
python mvp_main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### 5. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 📁 Project Structure

```
weekend-rag-system/
├── backend/                 # FastAPI backend
│   ├── mvp_main.py         # Main backend application
│   ├── demo_main.py        # Demo version (no external APIs)
│   ├── requirements.txt    # Python dependencies
│   └── .env               # Environment variables
├── frontend/               # Next.js frontend
│   ├── src/app/           # App router pages
│   ├── package.json       # Node.js dependencies
│   └── next.config.ts     # Next.js configuration
├── supabase_setup.sql     # Database schema
├── setup.sh               # Setup script
├── start_servers.sh       # Server startup script
└── README.md              # This file
```

## 🔧 Development

### Backend Development

The backend uses FastAPI with the following key components:

- **Document Processing**: PDF and TXT file upload and text extraction
- **Text Chunking**: Intelligent text splitting with overlap
- **Vector Embeddings**: Google Gemini embeddings for semantic search
- **Vector Search**: Supabase pgvector for similarity search
- **AI Generation**: Google Gemini models for responses

### Frontend Development

The frontend is built with Next.js 15 and includes:

- **Modern UI**: Tailwind CSS for styling
- **File Upload**: Drag-and-drop file upload interface
- **Real-time Chat**: Interactive chat interface
- **Document Management**: View and manage uploaded documents
- **Responsive Design**: Works on desktop and mobile

### Database Schema

The system uses three main tables:

1. **documents**: Stores document metadata
2. **document_chunks**: Stores text chunks with vector embeddings
3. **conversations**: Stores chat history

## 🧪 Testing

### Test with Sample Document

1. Upload the included `test_document.txt`
2. Ask questions like:
   - "What is artificial intelligence?"
   - "Explain machine learning"
   - "What is deep learning?"

### API Testing

Test the backend API directly:

```bash
# Health check
curl http://localhost:8000/

# Upload document
curl -X POST -F "file=@test_document.txt" http://localhost:8000/upload

# Get documents
curl http://localhost:8000/documents

# Chat with documents
curl -X POST -H "Content-Type: application/json" \
  -d '{"message":"What is AI?"}' \
  http://localhost:8000/chat
```

## 🔒 Security Considerations

- **Environment Variables**: Never commit API keys to version control
- **File Validation**: Only PDF and TXT files are accepted
- **Rate Limiting**: Consider implementing rate limiting for production
- **Authentication**: Add proper authentication for production use

## 🚀 Deployment

### Frontend Deployment (Vercel)

1. Connect your GitHub repository to Vercel
2. Set environment variables in Vercel dashboard
3. Deploy automatically on push to main branch

### Backend Deployment (Railway/Render)

1. Create a new service from your GitHub repository
2. Set environment variables
3. Deploy the backend directory

### Database Deployment

Use Supabase's managed PostgreSQL service with pgvector extension.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

If you encounter any issues:

1. Check the console logs for both frontend and backend
2. Verify your environment variables are set correctly
3. Ensure Supabase database is properly configured
4. Check that all dependencies are installed

## 🎯 Roadmap

- [ ] Add authentication and user management
- [ ] Support for more file types (DOCX, MD)
- [ ] Real-time collaborative features
- [ ] Advanced document analytics
- [ ] Multi-language support
- [ ] Mobile app development
EOF

print_success "README created with comprehensive documentation"

# Create a simple test script
print_status "Creating test script..."
cat > test_system.py << 'EOF'
#!/usr/bin/env python3
"""
Test script for Weekend RAG System
"""

import requests
import time
import json

def test_backend():
    """Test the backend API"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Weekend RAG System...")
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend is running")
            print(f"   Response: {response.json()}")
        else:
            print("❌ Backend health check failed")
            return False
    except Exception as e:
        print(f"❌ Backend connection failed: {e}")
        return False
    
    # Test document upload
    try:
        with open("test_document.txt", "rb") as f:
            files = {"file": ("test_document.txt", f, "text/plain")}
            response = requests.post(f"{base_url}/upload", files=files)
            
        if response.status_code == 200:
            print("✅ Document upload successful")
            result = response.json()
            print(f"   Document ID: {result.get('document_id')}")
        else:
            print(f"❌ Document upload failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document upload error: {e}")
        return False
    
    # Test document listing
    try:
        response = requests.get(f"{base_url}/documents")
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents")
        else:
            print(f"❌ Document listing failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Document listing error: {e}")
        return False
    
    # Test chat functionality
    try:
        chat_data = {"message": "What is artificial intelligence?"}
        response = requests.post(
            f"{base_url}/chat",
            headers={"Content-Type": "application/json"},
            json=chat_data
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chat functionality working")
            print(f"   Response: {result.get('message', '')[:100]}...")
        else:
            print(f"❌ Chat failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Chat error: {e}")
        return False
    
    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    print("🚀 Weekend RAG System Test")
    print("=" * 40)
    
    # Wait for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(5)
    
    success = test_backend()
    
    if success:
        print("\n🎉 System is ready!")
        print("🌐 Frontend: http://localhost:3000")
        print("📊 Backend: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
    else:
        print("\n❌ System test failed. Please check the logs.")
EOF

chmod +x test_system.py

print_success "Test script created: test_system.py"

print_status "Setup complete! 🎉"
echo ""
echo "📋 Next steps:"
echo "1. Update backend/.env with your API keys"
echo "2. Set up your Supabase database using supabase_setup.sql"
echo "3. Run: ./start_servers.sh"
echo "4. Test the system: python test_system.py"
echo ""
echo "📚 Documentation: README.md"
echo "🧪 Test script: test_system.py"
echo "🚀 Startup script: start_servers.sh" 