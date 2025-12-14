"""Test ELI Core"""
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

print("Testing ELI Core initialization...")

try:
    from backend.eli_core import EliCore
    print("✅ EliCore imported")
    
    print("\nInitializing ELI...")
    eli = EliCore()
    print("✅ ELI initialized successfully!")
    
    print("\nELI is ready but not started (press Ctrl+C to exit)")
    print("To start ELI, run: python start_eli.py")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
