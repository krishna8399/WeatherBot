# WeatherBot - Quick Start Guide

## Prerequisites
- Python 3.8 or higher
- Internet connection

## Setup Instructions

### Step 1: Extract the Project
Extract the `WeatherBot_Upload.zip` file to a folder of your choice.

### Step 2: Set the Weather API Key

**Option A: Using the provided batch script (Recommended for Windows)**
1. Double-click `setup_api_key.bat`
2. Enter the API key when prompted: `309d537f8f4d4b5c8a9192738252411`
3. The script will set the environment variable and verify it's working

**Option B: Manual Setup (Windows)**
1. Open PowerShell or Command Prompt **as Administrator**
2. Run this command:
   ```
   setx WEATHERAPI_KEY "309d537f8f694e30a7283845252310"
   ```
3. Close and reopen your terminal for changes to take effect

**Option C: Manual Setup (Linux/Mac)**
1. Open terminal
2. Add to your `~/.bashrc` or `~/.zshrc`:
   ```bash
   export WEATHERAPI_KEY="309d537f8f694e30a7283845252310"
   ```
3. Run: `source ~/.bashrc` (or restart terminal)

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run the Bot

**Option 1: Interactive Chat (Terminal)**
```bash
rasa run actions &
rasa shell
```

**Option 2: Using the Web UI**
```bash
docker-compose up
```
Then open: http://localhost:8080

## Verify Installation

Run the test suite to ensure everything works:
```bash
pytest tests/test_actions.py -v
```

Expected output: All 3 tests should pass ✅

## Troubleshooting

### "API key not set" Error
- Make sure you completed Step 2 above
- Verify the key is set: 
  - Windows: `echo %WEATHERAPI_KEY%`
  - Linux/Mac: `echo $WEATHERAPI_KEY`
- If empty, repeat Step 2 and restart your terminal

### "Module not found" Errors
- Ensure you're in the project directory
- Run: `pip install -r requirements.txt`
- Set PYTHONPATH: 
  - Windows: `set PYTHONPATH=%CD%`
  - Linux/Mac: `export PYTHONPATH=$(pwd)`

### API Not Responding
- Check internet connection
- Verify API key is valid at: https://www.weatherapi.com/my/
- The provided key should work until its free tier limit is reached

## Contact
If you encounter any issues, please contact the project author.

---

**Included API Key (for evaluation purposes):**
```
309d537f8f694e30a7283845252310
```

**Note:** This is a free-tier API key with usage limits. For production use, please register for your own key at https://www.weatherapi.com/
