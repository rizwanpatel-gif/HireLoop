"""
Test if the OpenRouter API key is working properly
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_api_key():
    """Test if API key is loaded"""
    api_key = os.getenv('OPENROUTER_API_KEY')
    
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found in environment")
        return False
    
    if api_key.startswith('sk-or-v1-'):
        print(f"✅ OpenRouter API key found: {api_key[:20]}...")
        return True
    else:
        print(f"⚠️ API key format looks wrong: {api_key[:20]}...")
        return False

def test_ai_service():
    """Test AI service initialization"""
    try:
        from app.services.ai_service import AIService
        
        # Initialize with the free DeepSeek model
        ai_service = AIService(model="deepseek/deepseek-chat-v3-0324:free")
        
        print(f"✅ AI Service initialized successfully")
        print(f"   Model: {ai_service.model}")
        print(f"   API Key: {ai_service.api_key[:20]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ AI Service failed: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing API Configuration...")
    print("=" * 50)
    
    key_ok = test_api_key()
    if key_ok:
        ai_ok = test_ai_service()
        
        if ai_ok:
            print("🎉 All tests passed! API is ready to use.")
        else:
            print("🚨 AI service test failed")
    else:
        print("🚨 API key test failed")
