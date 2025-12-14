"""Test imports"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing imports...")

try:
    print("1. Importing voice engine...")
    from backend.voice.voice_engine import VoiceEngine
    print("✅ Voice engine imported")
except Exception as e:
    print(f"❌ Voice engine failed: {e}")
    import traceback
    traceback.print_exc()

try:
    print("2. Importing NLP processor...")
    from backend.ai.nlp_processor import NLPProcessor
    print("✅ NLP processor imported")
except Exception as e:
    print(f"❌ NLP processor failed: {e}")

try:
    print("3. Importing command executor...")
    from backend.command_executor import CommandExecutor
    print("✅ Command executor imported")
except Exception as e:
    print(f"❌ Command executor failed: {e}")

print("\nAll imports successful!")
