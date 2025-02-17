import http.server
import socketserver
import requests

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        url = f"http://10.0.11.2:8000{self.path}"
        response = requests.get(url)
        self.send_response(response.status_code)
        for k, v in response.headers.items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(response.content)

with socketserver.TCPServer(("0.0.0.0", 8888), ProxyHandler) as httpd:
    print("Proxy server listening on port 8888")
    httpd.serve_forever()
