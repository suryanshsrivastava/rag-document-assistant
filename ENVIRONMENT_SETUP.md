# Development Environment Setup

## Environment Overview
This document outlines the complete development environment setup for the weekend-rag-system project, including all tools and their versions for consistency across development environments.

## Core Technologies

### Python Environment
- **Python Version**: 3.12.3
- **Virtual Environment**: `venv` (located at `./venv/`)
- **Package Manager**: pip 25.1.1
- **Framework**: FastAPI 0.116.0
- **Server**: Uvicorn 0.35.0

### Node.js Environment
- **Node.js Version**: 20.19.3 (LTS)
- **NPM Version**: 10.8.2
- **Framework**: Next.js 15.3.5 (via create-next-app)

### Database Management
- **Supabase CLI**: 2.30.4
- **Installation Method**: Binary release from GitHub

### Development Tools
- **AI-Assisted IDE**: Cursor 1.2.4
- **Version Control**: Git 2.43.0
- **Operating System**: Linux (WSL2/Ubuntu-based)

## Setup Instructions

### 1. Python Virtual Environment Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install FastAPI and dependencies
pip install fastapi uvicorn
```

### 2. Node.js Setup
```bash
# Verify Node.js installation
node --version  # Should output v20.19.3

# Verify NPM installation
npm --version   # Should output 10.8.2

# Create Next.js app (when needed)
npx create-next-app@latest [project-name]
```

### 3. Supabase CLI Setup
```bash
# Install Supabase CLI (binary method)
curl -fsSL https://github.com/supabase/cli/releases/latest/download/supabase_linux_amd64.tar.gz | tar -xzO supabase > /tmp/supabase
sudo mv /tmp/supabase /usr/local/bin/supabase
sudo chmod +x /usr/local/bin/supabase

# Verify installation
supabase --version  # Should output 2.30.4
```

### 4. Development Environment Activation
```bash
# Always activate Python virtual environment before working
source venv/bin/activate

# Verify you're in the virtual environment
echo $VIRTUAL_ENV  # Should show path to venv
```

## Project Structure Recommendations

```
weekend-rag-system/
├── backend/                 # FastAPI backend
│   ├── app/
│   ├── requirements.txt
│   └── main.py
├── frontend/               # Next.js frontend
│   ├── src/
│   ├── package.json
│   └── next.config.js
├── database/              # Supabase configurations
│   ├── migrations/
│   └── seed.sql
├── venv/                  # Python virtual environment
├── .env                   # Environment variables
├── .gitignore
└── README.md
```

## Technology Stack Rationale

### FastAPI (Backend Framework)
**Chosen over Django/Flask for the following reasons:**
- **Performance**: Async/await support provides superior performance for I/O-bound operations
- **Modern Python**: Built-in support for Python 3.6+ type hints and modern language features
- **Automatic Documentation**: OpenAPI/Swagger docs generated automatically from code
- **Data Validation**: Pydantic integration provides robust request/response validation
- **Developer Experience**: Excellent IDE support and debugging capabilities

**Potential Tradeoffs:**
- Smaller ecosystem compared to Django
- Less mature ORM options (though SQLAlchemy integration is excellent)
- Fewer built-in features compared to Django's "batteries included" approach

### Next.js (Frontend Framework)
**Chosen over Create React App/Vite for the following reasons:**
- **Full-Stack Capabilities**: API routes enable backend functionality within the same framework
- **Performance**: Server-side rendering, static generation, and automatic optimization
- **Developer Experience**: Hot reloading, built-in TypeScript support, excellent debugging
- **Production Ready**: Built-in optimizations for images, fonts, and code splitting
- **Deployment**: Seamless integration with Vercel and other platforms

**Potential Tradeoffs:**
- Steeper learning curve for React beginners
- Build complexity can be overwhelming for simple projects
- Opinionated structure may not suit all project types

### Supabase (Database [0m[90m[39m[94m
Management)
**Chosen over traditional PostgreSQL + custom auth for the following reasons:**
- **Rapid Development**: Instant APIs, real-time subscriptions, and built-in auth
- **Modern Architecture**: Row-level security, edge functions, and GraphQL support
- **Developer Experience**: Excellent dashboard, CLI tools, and local development
- **Scalability**: Managed infrastructure with automatic scaling
- **Open Source**: Can be self-hosted if needed

**Potential Tradeoffs:**
- Vendor lock-in concerns (though open-source mitigates this)
- Less control over database optimizations
- Pricing can scale up with usage
- Learning curve for Supabase-specific features

### Cursor IDE (Development Environment)
**Chosen over VS Code for the following reasons:**
- **AI Integration**: Context-aware code completion and generation
- **Modern Interface**: Improved user experience and performance
- **Productivity**: AI-powered code explanations and refactoring
- **Compatibility**: Built on VS Code foundation with familiar extensions

**Potential Tradeoffs:**
- Proprietary software vs open-source VS Code
- Privacy concerns with AI features
- Potential subscription costs for advanced features
- Smaller community compared to VS Code

## Environment Consistency

### Python Dependencies
```

### Node.js Dependencies
The `package.json` file in the frontend directory will track all Node.js dependencies.

### Environment Variables
Create a `.env` file for sensitive configurations:
```env
# Database
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_supabase_anon_key

# API Configuration
API_PORT=8000
FRONTEND_URL=http://localhost:3000

# Development
DEBUG=true
```

## Development Workflow

1. **Start Development Session**:
   ```bash
   # Activate Python virtual environment
   source venv/bin/activate
   
   # Start FastAPI backend
   cd backend && uvicorn main:app --reload --port 8000
   
   # Start Next.js frontend (in another terminal)
   cd frontend && npm run dev
   ```

2. **Database Operations**:
   ```bash
   # Initialize Supabase project
   supabase init
   
   # Start local Supabase instance
   supabase start
   
   # Apply migrations
   supabase db reset
   ```

## Tool Rationale

### Technology Stack Decisions

1. **FastAPI over Django/Flask**: 
   - Superior performance with async support
   - Automatic API documentation with OpenAPI/Swagger
   - Type hints support for better code quality
   - Built-in data validation with Pydantic

2. **Next.js over Create React App**:
   - Server-side rendering capabilities
   - Built-in routing and optimization
   - Excellent TypeScript support
   - Superior developer experience

3. **Supabase over Traditional PostgreSQL**:
   - Instant APIs and real-time subscriptions
   - Built-in authentication and authorization
   - Edge functions for serverless compute
   - Simplified deployment and scaling

4. **Cursor IDE over VS Code**:
   - AI-powered code completion and generation
   - Context-aware suggestions
   - Integrated chat for code explanations
   - Better support for modern development workflows

## Potential Tradeoffs

### FastAPI
- **Pros**: High performance, modern Python features, automatic docs
- **Cons**: Smaller ecosystem compared to Django, less mature ORM options

### Next.js
- **Pros**: Full-stack capabilities, excellent performance, great DX
- **Cons**: Learning curve for React concepts, build complexity

### Supabase
- **Pros**: Rapid development, managed infrastructure, real-time features
- **Cons**: Vendor lock-in, less control over database optimizations

### Cursor IDE
- **Pros**: AI assistance, modern interface, great productivity
- **Cons**: Proprietary software, potential privacy concerns with AI features

## Next Steps

1. Initialize the project structure
2. Set up database schema in Supabase
3. Create basic FastAPI endpoints
4. Implement Next.js frontend components
5. Integrate authentication with Supabase
6. Deploy to production environment

---

*Last updated: 2025-01-12*
*Environment verified on: Linux (WSL2/Ubuntu)*
