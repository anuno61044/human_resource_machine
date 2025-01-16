from flask import Flask, request
import requests
import random
from flask_cors import CORS

app = Flask(__name__)
CORS(app, supports_credentials=True)

# Lista de IPs de los servidores backend
servers = [
    "http://10.0.11.2:8000",
    "http://10.0.11.3:8000",
]

@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
def route_request(path):
    if request.method == 'OPTIONS':
        return '', 200  # Responder a las solicitudes OPTIONS

    print(f"Received request: {request.method} /{path}")
    
    server = random.choice(servers)
    
    response = requests.request(
        method=request.method,
        url=f"{server}/{path}",
        headers={key: value for (key, value) in request.headers},
        data=request.get_data(),
        cookies=request.cookies,
        allow_redirects=False
    )

    return (response.content, response.status_code, response.headers.items())

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, OPTIONS, PUT, DELETE')
    return response

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)