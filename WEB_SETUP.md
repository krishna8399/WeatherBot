# WeatherBot Web Interface

## Quick Start

### Option 1: One-Click Launch (Recommended)
Double-click `start_bot.bat` to start all services automatically.

The script will:
1. Start the Rasa action server
2. Start the Rasa API server
3. Start the web interface
4. Open your browser to http://localhost:8080

### Option 2: Manual Launch

#### Step 1: Install Required Dependencies
```powershell
conda activate weather_env
pip install flask flask-cors
```

#### Step 2: Start Services (3 separate terminals)

**Terminal 1 - Action Server:**
```powershell
conda activate weather_env
rasa run actions
```

**Terminal 2 - Rasa Server:**
```powershell
conda activate weather_env
rasa run --enable-api --cors "*" --port 5005
```

**Terminal 3 - Web Interface:**
```powershell
conda activate weather_env
python web_server.py
```

#### Step 3: Access the Bot
Open your browser and go to: http://localhost:8080

## Sharing with Others

### Local Network Access
1. Find your computer's IP address:
   ```powershell
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. Share this URL with others on the same network:
   ```
   http://YOUR_IP:8080
   ```
   Example: http://192.168.1.100:8080

### Internet Access (using ngrok)
For external access beyond your local network:

1. Download and install ngrok: https://ngrok.com/download

2. Start ngrok tunnel:
   ```powershell
   ngrok http 8080
   ```

3. Share the public URL provided by ngrok (e.g., https://abc123.ngrok.io)

## Environment Variables

Make sure `WEATHERAPI_KEY` is set before starting:

```powershell
$env:WEATHERAPI_KEY = "your_api_key_here"
```

To set it permanently:
```powershell
setx WEATHERAPI_KEY "your_api_key_here"
```

## Troubleshooting

### "Cannot connect to server" error
- Make sure all 3 services are running
- Check that Rasa server is on port 5005: http://localhost:5005
- Verify no firewall is blocking the ports

### Web interface not loading
- Ensure Flask and flask-cors are installed: `pip install flask flask-cors`
- Check that port 8080 is not in use by another application

### Bot not responding
- Verify action server is running on port 5055
- Check WEATHERAPI_KEY environment variable is set
- Look for errors in the action server terminal

## Features

- 🎨 Modern, responsive chat interface
- 💬 Real-time messaging with typing indicators
- 🌐 Accessible via browser (no terminal needed)
- 📱 Mobile-friendly design
- 🔗 Shareable link for multiple users

## Architecture

```
User Browser (port 8080)
    ↓
Flask Web Server
    ↓
Rasa REST API (port 5005)
    ↓
Rasa Action Server (port 5055)
    ↓
WeatherAPI.com
```
