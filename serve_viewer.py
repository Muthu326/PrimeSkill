"""
Simple HTTP Server for Quick Scan Viewer
Serves static files and JSON data over HTTP for public access
"""
import http.server
import socketserver
import os
import sys
from pathlib import Path

# Configuration
PORT = 8080
DIRECTORY = Path(__file__).parent

class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """Custom handler with CORS support"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)
    
    def end_headers(self):
        """Add CORS headers to allow cross-origin requests"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.log_date_time_string()}] {format % args}")

def get_local_ip():
    """Get local IP address"""
    import socket
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "localhost"

def main():
    """Start the HTTP server"""
    os.chdir(DIRECTORY)
    
    # Create handler
    Handler = CustomHTTPRequestHandler
    
    # Try different ports if 8080 is taken
    current_port = PORT
    max_tries = 10
    httpd = None
    
    for i in range(max_tries):
        try:
            # Set allow_reuse_address on the class level for socketserver
            socketserver.TCPServer.allow_reuse_address = True
            httpd = socketserver.TCPServer(("", current_port), Handler)
            break
        except OSError as e:
            if e.errno == 10048: # Port already in use
                print(f"⚠️  Port {current_port} is already in use. Trying next port...")
                current_port += 1
            else:
                raise e
    
    if not httpd:
        print(f"❌ Could not find an available port after {max_tries} attempts.")
        sys.exit(1)

    with httpd:
        local_ip = get_local_ip()
        
        print("=" * 60)
        print("🚀 Quick Scan Viewer Server Started!")
        print("=" * 60)
        print(f"\n📍 Access URLs:")
        print(f"   Local:    http://localhost:{current_port}/static/scan_viewer.html")
        print(f"   Network:  http://{local_ip}:{current_port}/static/scan_viewer.html")
        print(f"\n📊 JSON Data:")
        print(f"   http://localhost:{current_port}/data/scan_cache.json")
        print(f"\n💡 Share the Network URL with others on your WiFi")
        print(f"💡 For internet access, use ngrok or cloudflared")
        print(f"\n⏹️  Press Ctrl+C to stop server")
        print("=" * 60)
        print()
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n🛑 Server stopped by user")
            sys.exit(0)

if __name__ == "__main__":
    main()
