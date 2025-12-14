import logging
import time
from backend.ai.llm_integration import LLMIntegration

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_llm():
    print("\n" + "="*50)
    print("🧠 Testing Local LLM (Ollama) Integration")
    print("="*50)
    
    config = {
        "llm_model": "phi3",
        "llm_api_url": "http://localhost:11434/api/generate"
    }
    
    try:
        print("\n[1/3] Initializing LLM Integration...")
        llm = LLMIntegration(config)
        
        if llm.available:
            print(f"✅ Ollama detected! Model: {llm.model_name}")
            
            print("\n[2/3] Generating Check")
            print("Asking: 'Hello, are you there?'")
            start_time = time.time()
            response = llm.generate_response("Hello, are you there?")
            print(f"Response ({time.time() - start_time:.2f}s): {response}")
            
            if response and "Error" not in response:
                print("✅ Generation successful")
            else:
                print("⚠️ Generation failed or returned error")
        else:
            print("❌ Ollama NOT detected on localhost:11434")
            print("Action Required: Install Ollama from https://ollama.com/ and run 'ollama run phi3'")
            
        print("\nDone.")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_llm()
