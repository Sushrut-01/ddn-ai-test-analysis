#!/usr/bin/env python3
"""
Simple HTTP server for DDN Dashboard
Works with any Python 3.x installation
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

PORT = 8080

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

    def log_message(self, format, *args):
        # Colorful logging
        print(f"[SERVER] {format % args}")

def main():
    # Change to dashboard directory
    dashboard_path = Path(__file__).parent / "implementation" / "dashboard-ui"

    if dashboard_path.exists():
        os.chdir(dashboard_path)
        print(f"[INFO] Serving from: {dashboard_path}")
    else:
        # Serve the simple HTML from root
        print("[INFO] Dashboard source not found, serving from root")

    handler = MyHTTPRequestHandler

    print("\n" + "="*60)
    print("  DDN AI DASHBOARD - SIMPLE SERVER")
    print("="*60)
    print(f"\n[✓] Server starting on port {PORT}...")

    try:
        with socketserver.TCPServer(("", PORT), handler) as httpd:
            url = f"http://localhost:{PORT}"
            print(f"\n[✓] Dashboard available at: {url}")
            print(f"[✓] Opening browser...")

            # Try to open browser
            try:
                webbrowser.open(url)
                print(f"[✓] Browser opened!")
            except:
                print(f"[!] Could not auto-open browser")
                print(f"[!] Please manually open: {url}")

            print(f"\n{'='*60}")
            print(f"  SERVER RUNNING")
            print(f"{'='*60}")
            print(f"\n[INFO] Press Ctrl+C to stop the server\n")

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n[✓] Server stopped by user")
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n[X] Port {PORT} is already in use!")
            print(f"[!] Try closing other programs or use a different port")
            print(f"\n[FIX] Kill the process using port {PORT}:")
            print(f"      netstat -ano | findstr :{PORT}")
            print(f"      taskkill /F /PID <PID>")
        else:
            print(f"\n[X] Error: {e}")
    except Exception as e:
        print(f"\n[X] Unexpected error: {e}")

if __name__ == "__main__":
    main()
