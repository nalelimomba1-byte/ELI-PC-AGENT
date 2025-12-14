import requests
import logging
import json

logger = logging.getLogger(__name__)

class LLMIntegration:
    """
    Integrates with Local LLM via Ollama.
    Recommended Model: phi3 (3.8GB)
    """
    
    def __init__(self, config=None, model_name="phi3", api_url="http://localhost:11434/api/generate"):
        if isinstance(config, dict):
            self.model_name = config.get("llm_model", model_name)
            self.api_url = config.get("llm_api_url", api_url)
        else:
            self.model_name = model_name
            self.api_url = api_url
            
        self.available = self.check_availability()
        
    def check_availability(self):
        """Check if Ollama is running"""
        try:
            # Simple check to root or tags endpoint
            res = requests.get("http://localhost:11434/", timeout=2)
            if res.status_code == 200:
                logger.info(f"Ollama detected (Model: {self.model_name})")
                return True
        except:
            logger.warning("Ollama not detected running on localhost:11434")
            return False
        return False

    def generate_response(self, prompt, system_prompt="You are ANNY, a helpful desktop assistant. Keep answers concise."):
        """
        Generate response from LLM
        """
        if not self.available:
            self.available = self.check_availability()
            if not self.available:
                return "I'm sorry, my AI brain (Ollama) is not running."

        full_prompt = f"{system_prompt}\n\nUser: {prompt}\nAssistant:"
        
        payload = {
            "model": self.model_name,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_ctx": 2048
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            else:
                logger.error(f"Ollama Error: {response.text}")
                return "Error querying AI."
                
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            return "I encountered an error thinking about that."
