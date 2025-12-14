"""
Test pyttsx3 voice output
"""

import pyttsx3

print("Testing pyttsx3 voice...")

try:
    engine = pyttsx3.init()
    
    # Set properties
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 1.0)
    
    # Get available voices
    voices = engine.getProperty('voices')
    print(f"Available voices: {len(voices)}")
    
    # Test speech
    print("Speaking: 'Hello, this is ELI testing voice output'")
    engine.say("Hello, this is ELI testing voice output")
    engine.runAndWait()
    
    print("✅ Voice test complete! Did you hear it?")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

input("\nPress Enter to exit...")
