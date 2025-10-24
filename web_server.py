from flask import Flask, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')

@app.route('/')
def index():
    """Serve the main chat interface"""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve static files"""
    return send_from_directory(WEB_DIR, path)

if __name__ == '__main__':
    print("🌤️  WeatherBot Web Server Starting...")
    print("📍 Access the chat interface at: http://localhost:8080")
    print("🌐 Share this link with others on your network: http://<your-ip>:8080")
    print("\n💡 Tip: To find your IP address, run 'ipconfig' (Windows) or 'ifconfig' (Mac/Linux)")
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(host='0.0.0.0', port=8080, debug=False)
