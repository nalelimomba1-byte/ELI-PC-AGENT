"""
Simple ELI Starter - Runs backend with API server
"""

import sys
import threading
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Now import and run
from backend.eli_core import EliCore
from backend.api_server import run_server

def start_api_server(eli_instance):
    """Start Flask API server in a separate thread"""
    print("Starting API server on http://127.0.0.1:5000")
    run_server(eli_instance, host='127.0.0.1', port=5000)

if __name__ == "__main__":
    print("Starting ELI backend...")
    eli = EliCore()
    
    # Start API server in background thread
    api_thread = threading.Thread(target=start_api_server, args=(eli,), daemon=True)
    api_thread.start()
    
    print("\nELI is ready!")
    print("🌐 Web UI: Open web_ui.html in your browser")
    print("🎤 Voice: Say 'Hey ELI' to activate")
    print("\nPress Ctrl+C to shutdown\n")
    
    try:
        eli.start()
    except KeyboardInterrupt:
        eli.stop()
        print("\nELI shutdown complete")
