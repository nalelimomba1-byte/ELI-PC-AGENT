import logging
import time
from backend.voice.voice_engine import VoiceEngine

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_piper():
    print("\n" + "="*50)
    print("🗣️ Testing Piper TTS Integration")
    print("="*50)
    
    # Config
    voice_config = {"engine": "piper"} # Should default to piper anyway if available
    speech_config = {}
    
    try:
        print("\n[1/2] Initializing Voice Engine...")
        engine = VoiceEngine(voice_config, speech_config)
        
        if engine.tts_engine == 'piper':
            print("✅ Piper TTS Engine active")
        else:
            print(f"❌ Warning: Engine is using {engine.tts_engine}")
            
        print("\n[2/2] Speaking Test")
        text = "Hello! This is a test of the Piper Text to Speech system."
        print(f"Speaking: '{text}'")
        
        start_time = time.time()
        engine.speak(text)
        print(f"✅ Speech completed in {time.time() - start_time:.2f}s")
        
        print("\nDone.")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_piper()
