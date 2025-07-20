import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = "public"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

os.chdir(os.path.dirname(os.path.realpath(__file__)))

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving v1 at http://localhost:{PORT}")
    httpd.serve_forever()