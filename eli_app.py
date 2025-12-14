"""
ELI Simple Launcher - Just opens web UI, backend runs separately
"""

import webview
import time
from pathlib import Path

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║                    ELI - Ready                            ║
    ║         Enhanced Learning Intelligence                     ║
    ╚═══════════════════════════════════════════════════════════╝
    
    ✅ Make sure backend is running: python start_eli.py
    🌐 Opening ELI interface...
    """)
    
    # Wait a moment
    time.sleep(1)
    
    # Get path to web UI
    ui_path = Path(__file__).parent / 'web_ui.html'
    
    # Create native app window
    window = webview.create_window(
        'ELI - Enhanced Learning Intelligence',
        str(ui_path.absolute()),
        width=900,
        height=1100,
        resizable=True,
        background_color='#000000'
    )
    
    # Start the app
    webview.start(debug=False)

if __name__ == "__main__":
    main()
