#!/usr/bin/env python3
"""
Simple script to test environment variable loading
"""

import os
from dotenv import load_dotenv

def test_env_loading():
    """Test if environment variables are loaded correctly"""
    print("Testing environment variable loading...")
    
    # Load environment variables
    load_dotenv()
    
    # Check Supabase configuration
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    print(f"SUPABASE_URL: {supabase_url}")
    print(f"SUPABASE_ANON_KEY: {supabase_key[:20] + '...' if supabase_key and supabase_key != 'your_supabase_anon_key_here' else 'NOT SET'}")
    
    # Check Google API configuration
    google_key = os.getenv("GOOGLE_API_KEY")
    print(f"GOOGLE_API_KEY: {google_key[:20] + '...' if google_key and google_key != 'your_google_api_key_here' else 'NOT SET'}")
    
    # Check other configuration
    print(f"DEBUG: {os.getenv('DEBUG', 'NOT SET')}")
    print(f"LOG_LEVEL: {os.getenv('LOG_LEVEL', 'NOT SET')}")
    
    # Validation
    if not supabase_url or supabase_url == "your_supabase_url_here":
        print("❌ SUPABASE_URL not configured properly")
        return False
    
    if not supabase_key or supabase_key == "your_supabase_anon_key_here":
        print("❌ SUPABASE_ANON_KEY not configured properly")
        return False
    
    if not google_key or google_key == "your_google_api_key_here":
        print("❌ GOOGLE_API_KEY not configured properly")
        return False
    
    print("✅ All environment variables are configured correctly!")
    return True

if __name__ == "__main__":
    test_env_loading()
