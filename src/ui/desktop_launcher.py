#!/usr/bin/env python3
"""
Desktop launcher for MAGI Pipeline web UI
Launches the web UI and opens it in a web browser or native window
"""

import sys
import webbrowser
import threading
import time
import platform
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.web_ui import WebUI


def open_browser(url, delay=2):
    """Open browser after a delay to let the server start"""
    time.sleep(delay)
    print(f"Opening browser at {url}")
    webbrowser.open(url)


def main():
    """Main entry point for desktop application"""
    import argparse
    
    parser = argparse.ArgumentParser(description='MAGI Pipeline Desktop Application')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    parser.add_argument('--no-browser', action='store_true', help='Do not open browser automatically')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("MAGI Pipeline Desktop Application")
    print("=" * 60)
    print()
    print(f"Platform: {platform.system()}")
    print(f"Python: {sys.version}")
    print()
    print("Starting web server...")
    
    # Create web UI instance
    web_ui = WebUI()
    
    # URL to open
    url = f"http://{args.host}:{args.port}"
    
    # Open browser if not disabled
    if not args.no_browser:
        browser_thread = threading.Thread(target=open_browser, args=(url,))
        browser_thread.daemon = True
        browser_thread.start()
    
    print()
    print(f"Web UI available at: {url}")
    print(f"MAGI Viewer: {url}/viewer/viewer")
    print(f"About MAGI: {url}/about.html")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Run the web UI
    try:
        web_ui.run(
            host=args.host,
            port=args.port,
            reload=args.debug,
            log_level="debug" if args.debug else "info"
        )
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())