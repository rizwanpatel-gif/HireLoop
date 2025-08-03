"""
Free AI Models Usage Example
============================

This script demonstrates how to use the free AI models in your RHero system.
"""

import os
import asyncio
from backend.app.services.ai_service import AIService
from backend.app.services.free_ai_models import FreeAIModel, get_model_for_component

async def test_free_models():
    """
    Test different free models for various tasks
    """
    # Set your OpenRouter API key (get it from https://openrouter.ai/keys)
    api_key = os.getenv('OPENROUTER_API_KEY', 'your_api_key_here')
    
    if api_key == 'your_api_key_here':
        print("⚠️  Please set your OPENROUTER_API_KEY environment variable")
        print("   Get your free API key from: https://openrouter.ai/keys")
        return
    
    print("🚀 Testing Free AI Models for RHero Interview System")
    print("=" * 60)
    
    # Test 1: Candidate Analysis with Meta Llama
    print("\n1️⃣ Testing Candidate Analysis (Meta Llama 3.1 8B)")
    print("-" * 50)
    
    llama_service = AIService(
        api_key=api_key,
        model=FreeAIModel.LLAMA_3_1_8B.value
    )
    
    # Test with a simple candidate analysis prompt
    test_prompt = """
    Analyze this candidate profile:
    
    Name: John Doe
    Experience: 3 years Python development
    Skills: Python, FastAPI, PostgreSQL, Docker
    Education: Computer Science Degree
    
    Rate the candidate's suitability for a Senior Python Developer position (1-10) and explain why.
    """
    
    try:
        response = llama_service._make_api_call([
            {"role": "user", "content": test_prompt}
        ])
        print(f"✅ Meta Llama Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error with Meta Llama: {e}")
    
    # Test 2: Technical Analysis with DeepSeek
    print("\n2️⃣ Testing Technical Analysis (DeepSeek Chat)")
    print("-" * 50)
    
    deepseek_service = AIService(
        api_key=api_key,
        model=FreeAIModel.DEEPSEEK_CHAT.value
    )
    
    tech_prompt = """
    Evaluate the technical complexity of this interview question:
    
    "Implement a rate limiter that can handle 1000 requests per minute per user. 
    Consider distributed systems and Redis for storage."
    
    Rate difficulty (1-10) and suggest follow-up questions.
    """
    
    try:
        response = deepseek_service._make_api_call([
            {"role": "user", "content": tech_prompt}
        ])
        print(f"✅ DeepSeek Response: {response[:200]}...")
    except Exception as e:
        print(f"❌ Error with DeepSeek: {e}")
    
    # Test 3: Fast Processing with Google Gemini Flash
    print("\n3️⃣ Testing Fast Processing (Google Gemini Flash)")
    print("-" * 50)
    
    gemini_service = AIService(
        api_key=api_key,
        model=FreeAIModel.GEMINI_FLASH.value
    )
    
    quick_prompt = "Summarize the key skills needed for a React Developer position in 2 sentences."
    
    try:
        response = gemini_service._make_api_call([
            {"role": "user", "content": quick_prompt}
        ])
        print(f"✅ Gemini Flash Response: {response}")
    except Exception as e:
        print(f"❌ Error with Gemini Flash: {e}")
    
    # Test 4: Dynamic Model Selection
    print("\n4️⃣ Testing Dynamic Model Selection")
    print("-" * 50)
    
    adaptive_service = AIService(api_key=api_key)
    
    # Test different tasks with optimal models
    tasks_and_prompts = [
        ("candidate_analysis", "Rate this candidate's problem-solving skills based on their portfolio."),
        ("technical_analysis", "Explain the complexity of implementing microservices architecture."),
        ("code_analysis", "Review this Python function for efficiency and best practices."),
        ("fast_processing", "What's the most important skill for a data scientist?")
    ]
    
    for task_type, prompt in tasks_and_prompts:
        print(f"\n🔄 Testing {task_type}...")
        
        # Dynamically select the best model for this task
        adaptive_service.set_optimal_model_for_task(task_type)
        print(f"   Selected model: {adaptive_service.model}")
        
        try:
            response = adaptive_service._make_api_call([
                {"role": "user", "content": prompt}
            ])
            print(f"   ✅ Response: {response[:100]}...")
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    # Show available free models
    print("\n5️⃣ Available Free Models")
    print("-" * 50)
    
    free_models = adaptive_service.get_available_free_models()
    for model_name, config in free_models.items():
        print(f"📱 {model_name}")
        print(f"   Best for: {config.get('best_for', 'general tasks')}")
        print(f"   Cost: FREE! 💰")
        print()

def setup_environment():
    """
    Setup instructions for using free models
    """
    print("🔧 Setup Instructions for Free AI Models")
    print("=" * 50)
    print()
    print("1. Get a free OpenRouter API key:")
    print("   🔗 Visit: https://openrouter.ai/keys")
    print("   📝 Sign up (it's free!)")
    print("   🔑 Copy your API key")
    print()
    print("2. Set your environment variable:")
    print("   💻 Windows: set OPENROUTER_API_KEY=your_key_here")
    print("   💻 Linux/Mac: export OPENROUTER_API_KEY=your_key_here")
    print()
    print("3. Or update your .env file:")
    print("   📄 Add: OPENROUTER_API_KEY=your_key_here")
    print()
    print("4. Available FREE models:")
    for model in FreeAIModel:
        print(f"   🤖 {model.value}")
    print()
    print("5. The system will automatically use free models!")
    print("   💡 No charges, no credit card required for these models")
    print()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_environment()
    else:
        asyncio.run(test_free_models())
