import http.server
import socketserver
import os

def run_server():
    PORT = 5000
    Handler = http.server.SimpleHTTPRequestHandler
    
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving at port {PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    # Create a test file
    with open("index.html", "w") as f:
        f.write("<html><body><h1>Test Server Working</h1></body></html>")
    run_server()
