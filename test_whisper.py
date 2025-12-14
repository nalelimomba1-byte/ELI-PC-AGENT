import logging
import time
from backend.voice.voice_engine import VoiceEngine

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def test_whisper():
    print("\n" + "="*50)
    print("🎤 Testing Faster-Whisper Integration")
    print("="*50)
    
    # Config
    voice_config = {"engine": "pyttsx3"} # Use internal TTS for now
    speech_config = {
        "engine": "whisper", # This config key isn't used yet but good for future
        "energy_threshold": 3000,
        "pause_threshold": 0.8
    }
    
    try:
        print("\n[1/3] Initializing Voice Engine (Loading Model)...")
        start_time = time.time()
        engine = VoiceEngine(voice_config, speech_config)
        print(f"✅ Engine initialized in {time.time() - start_time:.2f}s")
        
        # Check if model loaded
        if hasattr(engine, 'whisper_model'):
            print(f"✅ Faster-Whisper model loaded on device: {engine.whisper_model.device}")
        else:
            print("❌ Faster-Whisper model NOT found!")
            return
            
        print("\n[2/3] Testing Transcription")
        print("Please speak a short phrase (e.g., 'Hello world') into your microphone...")
        print("Listening for 5 seconds...")
        
        text = engine.listen(timeout=5)
        
        if text:
            print(f"\n✅ Transcription Success!")
            print(f"You said: '{text}'")
        else:
            print("\n⚠️ No speech detected or transcription failed (this is normal if you didn't speak).")
            
        print("\n[3/3] Cleanup")
        # engine.stop() # Not strictly implemented yet
        print("Done.")
        
    except Exception as e:
        print(f"\n❌ Test Failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_whisper()
