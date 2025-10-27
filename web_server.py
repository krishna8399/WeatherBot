"""
Minimal Flask server to host the WeatherBot web UI.

Why a Flask server?
- It serves the static assets (HTML/CSS/JS) from the local "web" folder.
- It enables CORS to allow the UI to call the Rasa REST API on a different port (5005).
- It binds on 0.0.0.0 so the page is reachable via localhost and LAN IP (for demos).
"""

from flask import Flask, send_from_directory
from flask_cors import CORS
import os

# Create a Flask app instance
app = Flask(__name__)

# Enable Cross-Origin Resource Sharing so the browser can call Rasa on port 5005
CORS(app)

# Resolve the "web" directory relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WEB_DIR = os.path.join(BASE_DIR, 'web')

@app.route('/')
def index():
    """Serve the main chat interface (index.html)."""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    """Serve any other static file (CSS/JS/images) from the web folder."""
    return send_from_directory(WEB_DIR, path)

if __name__ == '__main__':
    # Friendly startup messages visible in the terminal
    print("🌤️  WeatherBot Web Server Starting...")
    print("📍 Access the chat interface at: http://localhost:8080")
    print("🌐 Share this link with others on your network: http://<your-ip>:8080")
    print("\n💡 Tip: To find your IP address, run 'ipconfig' (Windows) or 'ifconfig' (Mac/Linux)")
    print("\nPress Ctrl+C to stop the server\n")

    # Bind on all interfaces for localhost and LAN access
    app.run(host='0.0.0.0', port=8080, debug=False)
