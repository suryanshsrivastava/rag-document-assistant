# Weekend RAG System

A complete Retrieval-Augmented Generation (RAG) system built with Next.js, FastAPI, and Supabase.

## Features

- **Document Upload**: Support for PDF, DOCX, and TXT files with drag-and-drop interface
- **Vector Storage**: Store document embeddings in Supabase
- **Intelligent Text Processing**: Automatic text extraction, chunking, and embedding generation
- **Vector Search**: Semantic search across document chunks using embeddings
- **AI Chat Interface**: Real-time conversations with document context using Google Gemini
- **Source Citations**: See which documents and sections were used to generate responses
- **Document Management**: View, select, and manage uploaded documents
- **Modern UI**: Beautiful, responsive interface with dark mode support
- **Real-time Processing**: Fast document processing and chunking

## Technology Stack

- **Frontend**: Next.js 15 with TypeScript and Tailwind CSS
- **Backend**: FastAPI with Python
- **Database**: Supabase with PostgreSQL and pgvector
- **AI**: Google Gemini for embeddings and chat completions
- **File Processing**: PyPDF2, python-docx for document extraction

## Prerequisites

- Python 3.8+
- Node.js 18+
- Supabase account
- Google Gemini API key

## Quick Start

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
SUPABASE_KEY=your_supabase_anon_key_here
GEMINI_API_KEY=your_gemini_api_key_here
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

## Project Structure

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

## Development

### Backend Development

The backend uses FastAPI with the following key components:

- **Document Processing**: PDF and TXT file upload and text extraction
- **Text Chunking**: Intelligent text splitting with overlap
- **Vector Embeddings**: OpenAI embeddings for semantic search
- **Vector Search**: Supabase pgvector for similarity search
- **AI Generation**: OpenAI GPT-3.5-turbo for responses

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

## Roadmap

- [ ] Add authentication and user management
- [ ] Support for more file types (MD, XLSX)
- [ ] Real-time collaborative features
- [ ] Advanced document analytics
- [ ] Multi-language support
- [ ] Mobile app development
