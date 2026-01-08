from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        message = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Machine Sound Diagnostics</title>
            <meta http-equiv="refresh" content="0; url=https://your-huggingface-space.hf.space">
        </head>
        <body>
            <p>Redirecting to Hugging Face Space...</p>
        </body>
        </html>
        """
        self.wfile.write(message.encode())
        return 
