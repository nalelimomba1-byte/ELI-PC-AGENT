import os
import logging
import io
from dotenv import load_dotenv
from backend.ai.llm_integration import LLMIntegration

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini():
    print("--- Testing Gemini Integration ---")
    
    # 1. Load environment variables
    load_dotenv('backend/.env')
    api_key = os.getenv('GOOGLE_API_KEY')
    
    if not api_key:
        print("❌ Error: GOOGLE_API_KEY not found in backend/.env")
        return
        
    print(f"✅ Found API Key: {api_key[:5]}...{api_key[-5:]}")
    
    # 2. Initialize LLM
    config = {
        'provider': 'google',
        'model': 'gemini-pro',
        'api_key': api_key
    }
    
    # Capture logs
    log_capture_string = io.StringIO()
    ch = logging.StreamHandler(log_capture_string)
    ch.setLevel(logging.ERROR)
    logging.getLogger().addHandler(ch) # Attach to root logger
    
    try:
        llm = LLMIntegration(config)
        print("✅ LLMIntegration initialized")
    except Exception as e:
        print(f"❌ Failed to initialize LLMIntegration: {e}")
        return

    # 3. Test Text Generation
    print("\nTesting Text Generation...")
    try:
        response = llm.generate_response("Hello, are you working?")
        
        # Check logs for errors
        log_contents = log_capture_string.getvalue()
        if log_contents:
            print(f"\n❌ LOGGED ERRORS:\n{log_contents}")
            
        if response and "access to advanced AI" not in response and "error" not in response.lower():
             print(f"✅ Text Generation Working! Response: {response}")
        else:
             print(f"⚠️ Text Generation Warning: {response}")
    except Exception as e:
        print(f"❌ Text Generation Failed: {e}")

if __name__ == "__main__":
    test_gemini()
