#!/usr/bin/env python3
"""
Simple HTTP Server to test connectivity and serve QUIZDOM
"""

import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

# Change to the correct directory
os.chdir('/workspace')

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            # Serve the main QUIZDOM page
            self.path = '/templates/index.html'
        elif self.path.startswith('/static/'):
            # Serve static files
            pass
        elif self.path == '/OPEN_THIS.html':
            # Serve the access page
            pass
        
        return super().do_GET()

if __name__ == "__main__":
    PORT = 8080
    
    print("=" * 60)
    print("🎯 QUIZDOM Simple Server Starting...")
    print("=" * 60)
    print(f"📡 Server running on ALL these URLs:")
    print(f"   • http://localhost:{PORT}")
    print(f"   • http://127.0.0.1:{PORT}")
    print(f"   • http://0.0.0.0:{PORT}")
    print("=" * 60)
    print("📁 Files available:")
    print(f"   • Main App: http://localhost:{PORT}/templates/index.html")
    print(f"   • Access Page: http://localhost:{PORT}/OPEN_THIS.html")
    print("=" * 60)
    print("🌐 Copy any of the URLs above and paste in your browser!")
    print("=" * 60)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🚀 Server started successfully on port {PORT}")
        print("Press Ctrl+C to stop the server")
        print("=" * 60)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Server stopped")