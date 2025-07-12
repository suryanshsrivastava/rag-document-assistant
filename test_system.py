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
