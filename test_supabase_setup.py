#!/usr/bin/env python3
"""
Test script to verify Supabase setup for Weekend RAG System
"""

import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

def test_supabase_connection():
    """Test Supabase connection"""
    print("🧪 Testing Supabase Setup...")
    
    # Check if environment variables are set
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    google_key = os.getenv("GOOGLE_API_KEY")
    
    if not supabase_url or supabase_url == "your_supabase_url_here":
        print("❌ SUPABASE_URL not configured in backend/.env")
        return False
    
    if not supabase_key or supabase_key == "your_supabase_anon_key_here":
    print("❌ SUPABASE_ANON_KEY not configured in backend/.env")
    return False
    
    if not google_key or google_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY not configured in backend/.env")
        return False
    
    print("✅ Environment variables are configured")
    
    # Test Supabase connection
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}"
        }
        
        # Test connection by querying documents table
        response = requests.get(
            f"{supabase_url}/rest/v1/documents",
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Supabase connection successful")
            documents = response.json()
            print(f"   Found {len(documents)} documents in database")
        else:
            print(f"❌ Supabase connection failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Supabase connection error: {e}")
        return False
    
    return True

def test_backend_with_supabase():
    """Test the backend with Supabase integration"""
    print("\n🧪 Testing Backend with Supabase...")
    
    base_url = "http://localhost:8000"
    
    # Test health check
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            result = response.json()
            if "demo" in result.get("message", "").lower():
                print("⚠️  Backend is running in demo mode")
                print("   Switch to mvp_main.py for full Supabase integration")
                return False
            else:
                print("✅ Backend is running with Supabase integration")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
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
            result = response.json()
            print("✅ Document upload successful")
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
    
    return True

def main():
    """Main test function"""
    print("🚀 Weekend RAG System - Supabase Setup Test")
    print("=" * 50)
    
    # Test Supabase connection
    supabase_ok = test_supabase_connection()
    
    if not supabase_ok:
        print("\n❌ Supabase setup incomplete!")
        print("Please complete the setup steps above.")
        return
    
    # Test backend integration
    backend_ok = test_backend_with_supabase()
    
    if backend_ok:
        print("\n🎉 Supabase setup is complete and working!")
        print("🌐 Frontend: http://localhost:3000")
        print("📊 Backend: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
    else:
        print("\n⚠️  Backend needs to be restarted with Supabase integration")
        print("Run: source venv/bin/activate && cd backend && python mvp_main.py")

if __name__ == "__main__":
    main() 