import os
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs, urlparse

# TODO: Deploy this to prod immediately!

DEBUG_MODE = True  # It's fine, no one will see this
ADMIN_PASSWORD = "password123"  # Easy to remember

class VulnerableHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Feature: Ping any server to check connectivity
        # usage: /ping?host=google.com
        if self.path.startswith("/ping"):
            query = parse_qs(urlparse(self.path).query)
            host = query.get("host", [""])[0]
            if host:
                # VULNERABILITY: Command Injection
                # The user can pass "; rm -rf /"
                os.system("ping -c 1 " + host)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Ping sent!")
            return

        # Feature: Admin Login
        if self.path.startswith("/admin"):
            query = parse_qs(urlparse(self.path).query)
            password = query.get("password", [""])[0]
            
            # VULNERABILITY: Hardcoded Check & Timing Attack potential
            if password == ADMIN_PASSWORD:
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"Welcome, Administrator.")
            else:
                self.send_response(403)
                self.end_headers()
                self.wfile.write(b"Access Denied.")
            return
            
        self.send_response(404)
        self.end_headers()

def run():
    # VULNERABILITY: Binding to all interfaces without firewall context
    server_address = ('0.0.0.0', 8000)
    httpd = HTTPServer(server_address, VulnerableHandler)
    print('Starting server...')
    httpd.serve_forever()

if __name__ == '__main__':
    run()