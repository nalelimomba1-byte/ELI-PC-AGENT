import sys
import threading
import logging
import signal
import os

# Ensure backend can be imported
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from desktop_ui.app import DesktopApp
from backend.eli_core import EliCore

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("anny.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("Launcher")

def main():
    logger.info("🚀 Launching ANNY (Phase 3 UI)...")
    
    # 1. Initialize Backend
    try:
        core = EliCore()
    except Exception as e:
        logger.critical(f"Failed to initialize Core: {e}")
        return

    # 2. Initialize UI
    app = DesktopApp(core_system=core)
    
    # 3. Connect Clean Shutdown
    def on_shutdown(signum=None, frame=None):
        logger.info("Shutdown signal received...")
        app.on_closing()
        
    signal.signal(signal.SIGINT, on_shutdown)
    signal.signal(signal.SIGTERM, on_shutdown)
    
    # 4. Start Backend in Background Thread
    # EliCore should benefit from running its loops in a separate thread
    backend_thread = threading.Thread(target=core.start, daemon=True)
    backend_thread.start()
    
    # 5. Start UI (Main Thread - Required for Tkinter)
    try:
        app.mainloop()
    except KeyboardInterrupt:
        on_shutdown()
    finally:
        core.stop()
        logger.info("Application terminated.")

if __name__ == "__main__":
    main()
