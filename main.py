import sys
import os
import multiprocessing
import uvicorn
import webbrowser
import threading
import traceback
from time import sleep

# Required for PyInstaller + multiprocessing
multiprocessing.freeze_support()

# Ensure we can import from current directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

def run_gui():
    try:
        import setup_gui
    except Exception as e:
        print(f"\n[ERROR] Failed to start Setup GUI: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

def run_server():
    try:
        from server import app, start_tcp_emu
        from core.config import HOST, WEB_PORT, EMU_TCP_PORT
        
        # Start the TCP Emulator in a background thread (it was missing in the previous build)
        print(f"[POS PRINTER] Starting TCP Emulator on port {EMU_TCP_PORT}...")
        threading.Thread(target=start_tcp_emu, daemon=True).start()
        
        # Start Browser after a short delay
        def open_browser():
            sleep(2)
            print(f"[POS PRINTER] Opening browser at http://localhost:{WEB_PORT}")
            webbrowser.open(f"http://localhost:{WEB_PORT}")
        
        threading.Thread(target=open_browser, daemon=True).start()

        print(f"[POS PRINTER] Starting Web Server on port {WEB_PORT}...")
        uvicorn.run(app, host=HOST, port=WEB_PORT, reload=False, log_level="info")
        
    except Exception as e:
        print(f"\n[CRITICAL ERROR] Server failed to start: {e}")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    print("========================================")
    print("      POS PRINTER SERVER PRO            ")
    print("========================================\n")
    
    # 1. Run Setup GUI
    run_gui()
    
    # 2. Run Server (blocks here)
    run_server()
