#!/usr/bin/env python3
"""
Simple API Test Script for RAG Backend

This script tests the backend API endpoints without requiring a frontend.
"""

import requests
import json
import os
import time
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
TEST_FILE = "test_document.txt"

def create_test_document():
    """Create a test document for upload."""
    content = """
Artificial Intelligence and Machine Learning

This document provides an overview of artificial intelligence and machine learning concepts.

Key Topics:
1. Natural Language Processing (NLP)
   - Text analysis and understanding
   - Language generation and translation
   - Sentiment analysis

2. Computer Vision
   - Image recognition and classification
   - Object detection and tracking
   - Image segmentation

3. Deep Learning
   - Neural networks and architectures
   - Training and optimization techniques
   - Applications in various domains

The field of AI continues to evolve rapidly with new breakthroughs in research and practical applications.
"""
    
    with open(TEST_FILE, "w") as f:
        f.write(content)
    
    print(f"✅ Created test document: {TEST_FILE}")

def test_health_check():
    """Test the health check endpoint."""
    print("\n🔍 Testing Health Check...")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"Root endpoint: {response.status_code} - {response.json()}")
        
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health endpoint: {response.status_code}")
        if response.status_code == 200:
            health_data = response.json()
            print(f"Status: {health_data.get('status')}")
            print(f"Database connected: {health_data.get('database_connected')}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Server not running. Start with: uvicorn app.main:app --reload")
        return False
    
    return True

def test_document_upload():
    """Test document upload functionality."""
    print("\n📄 Testing Document Upload...")
    
    if not os.path.exists(TEST_FILE):
        create_test_document()
    
    try:
        with open(TEST_FILE, "rb") as f:
            files = {"file": (TEST_FILE, f, "text/plain")}
            response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
        
        print(f"Upload response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Document uploaded successfully!")
            print(f"Document ID: {data.get('document_id')}")
            print(f"Filename: {data.get('filename')}")
            print(f"Status: {data.get('status')}")
            return data.get('document_id')
        else:
            print(f"❌ Upload failed: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Upload error: {str(e)}")
        return None

def test_chat_with_documents(document_id):
    """Test chat functionality with uploaded document."""
    print(f"\n💬 Testing Chat with Document {document_id}...")
    
    if not document_id:
        print("❌ No document ID provided")
        return
    
    try:
        chat_data = {
            "message": "What is this document about?",
            "document_ids": [document_id]
        }
        
        response = requests.post(f"{BASE_URL}/api/chat", json=chat_data)
        
        print(f"Chat response: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Chat successful!")
            print(f"Response: {data.get('response')[:100]}...")
            print(f"Sources: {len(data.get('sources', []))} sources found")
            print(f"Conversation ID: {data.get('conversation_id')}")
        else:
            print(f"❌ Chat failed: {response.text}")
            
    except Exception as e:
        print(f"❌ Chat error: {str(e)}")

def test_list_documents():
    """Test listing documents."""
    print("\n📋 Testing List Documents...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/documents")
        
        print(f"List response: {response.status_code}")
        if response.status_code == 200:
            documents = response.json()
            print(f"✅ Found {len(documents)} documents")
            for doc in documents:
                print(f"  - {doc.get('filename')} ({doc.get('status')})")
        else:
            print(f"❌ List failed: {response.text}")
            
    except Exception as e:
        print(f"❌ List error: {str(e)}")

def cleanup():
    """Clean up test files."""
    if os.path.exists(TEST_FILE):
        os.remove(TEST_FILE)
        print(f"🧹 Cleaned up {TEST_FILE}")

def main():
    """Run all tests."""
    print("🧪 RAG Backend API Testing")
    print("=" * 40)
    
    # Test 1: Health Check
    if not test_health_check():
        print("\n❌ Health check failed. Make sure server is running.")
        return
    
    # Test 2: Document Upload
    document_id = test_document_upload()
    
    # Test 3: Chat with Documents
    if document_id:
        test_chat_with_documents(document_id)
    
    # Test 4: List Documents
    test_list_documents()
    
    # Cleanup
    cleanup()
    
    print("\n🎉 Testing completed!")
    print("\n💡 Tips:")
    print("- Check the server logs for detailed information")
    print("- Use FastAPI docs at http://localhost:8000/docs")
    print("- Set up environment variables for full functionality")

if __name__ == "__main__":
    main() 