"""
JARVIS Launcher - Start all components
"""

import subprocess
import sys
import time
import os
from pathlib import Path

# Force UTF-8 encoding for Windows console (Fixes UnicodeEncodeError)
sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

def print_banner():
    """Print JARVIS banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║         ███████╗██╗     ██╗                              ║
    ║         ██╔════╝██║     ██║                              ║
    ║         █████╗  ██║     ██║                              ║
    ║         ██╔══╝  ██║     ██║                              ║
    ║         ███████╗███████╗██║                              ║
    ║         ╚══════╝╚══════╝╚═╝                              ║
    ║                                                           ║
    ║        Enhanced Learning Intelligence                     ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
    print("\n🚀 Initializing ELI AI Assistant...\n")

def check_dependencies():
    """Check if required dependencies are installed"""
    print("📦 Checking dependencies...")
    
    # Check Python packages (TTS is optional, we have fallback)
    required_packages = [
        'flask', 'speech_recognition', 'psutil', 
        'pyautogui', 'requests', 'pyttsx3'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ Missing Python packages: {', '.join(missing)}")
        print("   Run: pip install -r requirements.txt")
        return False
    
    print("✅ All Python dependencies installed")
    
    # Check for optional TTS
    try:
        __import__('TTS')
        print("✅ Coqui TTS available (voice cloning enabled)")
    except ImportError:
        print("⚠️  Coqui TTS not available (using pyttsx3 fallback)")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js installed: {result.stdout.strip()}")
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False
    
    return True

def start_backend():
    """Start Python backend"""
    print("\n🔧 Starting backend server...")
    backend_path = Path(__file__).parent / 'start_eli.py'
    
    # Log backend output to file
    log_file = open('backend.log', 'w', encoding='utf-8')
    
    process = subprocess.Popen(
        [sys.executable, str(backend_path)],
        stdout=log_file,
        stderr=log_file,
        text=True
    )
    
    time.sleep(2)  # Wait for backend to start
    
    if process.poll() is None:
        print("✅ Backend server started")
        return process
    else:
        print("❌ Backend failed to start")
        # Print error output
        stderr = process.stderr.read() if process.stderr else ""
        if stderr:
            print(f"Error: {stderr[:200]}")
        return None

def start_frontend():
    """Start Electron frontend"""
    print("\n🎨 Starting frontend UI...")
    frontend_path = Path(__file__).parent / 'frontend'
    
    # Check if node_modules exists
    if not (frontend_path / 'node_modules').exists():
        print("📦 Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_path, shell=True)
    
    process = subprocess.Popen(
        ['npm', 'start'],
        cwd=frontend_path,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    time.sleep(3)  # Wait for frontend to start
    
    if process.poll() is None:
        print("✅ Frontend UI started")
        return process
    else:
        print("❌ Frontend failed to start")
        return None

def main():
    """Main launcher"""
    print_banner()
    
    # Check dependencies
    if not check_dependencies():
        print("\n❌ Please install missing dependencies and try again")
        sys.exit(1)
    
    # Start backend
    backend_process = start_backend()
    if not backend_process:
        print("\n❌ Failed to start backend")
        sys.exit(1)
    
    # Start frontend
    frontend_process = start_frontend()
    if not frontend_process:
        print("\n⚠️ Failed to start frontend (UI will be unavailable)")
        print("   Backend is still running!")
        # backend_process.terminate()
        # sys.exit(1)
    
    print("\n" + "="*60)
    print("🎉 ELI is now online and ready to assist!")
    print("="*60)
    print("\n💡 Tips:")
    print("   - Say 'Hey ELI' to activate voice commands")
    print("   - Type commands in the UI input field")
    print("   - Check the system status panel for component health")
    print("\n⚠️  Press Ctrl+C to shutdown ELI\n")
    
    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if backend_process.poll() is not None:
                print("\n❌ Backend crashed!")
                break
            
            if frontend_process and frontend_process.poll() is not None:
                print("\n⚠️ Frontend UI crashed (Backend still running)")
                frontend_process = None
                # Don't break, allow backend to continue
                # break
    
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down ELI...")
        
        # Terminate processes
        if backend_process:
            backend_process.terminate()
            print("✅ Backend stopped")
        
        if frontend_process:
            frontend_process.terminate()
            print("✅ Frontend stopped")
        
        print("\n👋 ELI offline. See you next time!")

if __name__ == "__main__":
    main()
