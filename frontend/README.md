# RAG Document Assistant Frontend

A modern, responsive frontend for the RAG Document Assistant built with Next.js 15, TypeScript, and Tailwind CSS.

## Features

- **Document Upload**: Drag-and-drop file upload with support for PDF, DOCX, and TXT files
- **Document Management**: View, select, and delete uploaded documents
- **Chat Interface**: Real-time chat with AI using RAG technology
- **Source Citations**: View which documents were used to generate responses
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Mode Support**: Automatic dark/light mode based on system preferences

## Tech Stack

- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **React Hooks**: State management and side effects

## Components

- `DocumentUpload`: Drag-and-drop file upload with progress indicators
- `ChatInterface`: Real-time chat with message history and source citations
- `DocumentList`: Document management with selection and deletion
- `Notification`: Toast notifications for success/error messages

## API Integration

The frontend communicates with the FastAPI backend through a type-safe API client:

- Document upload and management
- Real-time chat with RAG-powered responses
- Health checks and error handling

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Environment Variables

Create a `.env.local` file in the frontend directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development

- `npm run dev`: Start development server
- `npm run build`: Build for production
- `npm run start`: Start production server
- `npm run lint`: Run ESLint

## Project Structure

```
src/
├── app/                 # Next.js App Router
│   ├── layout.tsx      # Root layout
│   ├── page.tsx        # Main dashboard
│   └── globals.css     # Global styles
├── components/          # React components
│   ├── DocumentUpload.tsx
│   ├── ChatInterface.tsx
│   ├── DocumentList.tsx
│   └── Notification.tsx
├── lib/                # Utility libraries
│   └── api.ts          # API client
└── types/              # TypeScript types
    └── api.ts          # API type definitions
```
