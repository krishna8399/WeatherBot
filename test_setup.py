"""
WeatherBot Diagnostic Test Script
Run this to verify everything is working before starting the bot.
"""

import sys
import os

print("=" * 60)
print("WeatherBot Diagnostic Test")
print("=" * 60)
print()

# Test 1: Python Version
print("[1/5] Checking Python version...")
print(f"   Python {sys.version}")
if sys.version_info < (3, 8):
    print("   ⚠️  WARNING: Python 3.8+ recommended")
else:
    print("   ✓ OK")
print()

# Test 2: Required Modules
print("[2/5] Checking required modules...")
required_modules = ['requests', 'rasa', 'rasa_sdk']
missing = []
for module in required_modules:
    try:
        __import__(module)
        print(f"   ✓ {module}")
    except ImportError:
        print(f"   ✗ {module} - MISSING")
        missing.append(module)

if missing:
    print(f"\n   ⚠️  Missing modules: {', '.join(missing)}")
    print("   Run: pip install -r requirements.txt")
else:
    print("   ✓ All modules installed")
print()

# Test 3: API Key
print("[3/5] Checking API key...")
sys.path.insert(0, os.path.dirname(__file__))
try:
    from actions.actions import _get_weatherapi_key
    api_key = _get_weatherapi_key()
    if api_key:
        print(f"   ✓ API key found: {api_key[:10]}...")
    else:
        print("   ✗ API key not found")
        print("   Set WEATHERAPI_KEY environment variable")
except Exception as e:
    print(f"   ⚠️  Could not load actions module: {e}")
    api_key = "309d537f8f694e30a7283845252310"  # Fallback
    print(f"   Using hardcoded key: {api_key[:10]}...")
print()

# Test 4: API Connection
print("[4/5] Testing WeatherAPI connection...")
try:
    import requests
    url = f"http://api.weatherapi.com/v1/current.json?key={api_key}&q=London"
    response = requests.get(url, timeout=10)
    
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✓ API Working!")
        print(f"   Sample: {data['location']['name']}, {data['current']['temp_c']}°C")
    elif response.status_code == 401:
        print("   ✗ API Key Invalid (401 Unauthorized)")
        print("   The API key may have expired. Please get a new one from:")
        print("   https://www.weatherapi.com/signup.aspx")
    elif response.status_code == 403:
        print("   ✗ API Access Forbidden (403)")
        print("   Possible causes:")
        print("   - Free tier limit reached")
        print("   - IP/Region blocked by WeatherAPI")
        print("   - Firewall blocking the request")
        print("   Try: Get a new free key at https://www.weatherapi.com/signup.aspx")
    else:
        print(f"   ✗ Unexpected error: {response.status_code}")
        print(f"   Response: {response.text[:200]}")
        
except requests.exceptions.ConnectionError:
    print("   ✗ Connection Error")
    print("   Check your internet connection")
except requests.exceptions.Timeout:
    print("   ✗ Request Timeout")
    print("   WeatherAPI may be slow or unreachable")
except Exception as e:
    print(f"   ✗ Error: {e}")
print()

# Test 5: Model Check
print("[5/5] Checking for trained model...")
models_dir = "models"
if os.path.exists(models_dir):
    models = [f for f in os.listdir(models_dir) if f.endswith('.tar.gz')]
    if models:
        print(f"   ✓ Found {len(models)} trained model(s)")
        print(f"   Latest: {sorted(models)[-1]}")
    else:
        print("   ✗ No trained models found")
        print("   Run: rasa train")
else:
    print("   ✗ models/ directory not found")
print()

# Summary
print("=" * 60)
print("Summary")
print("=" * 60)

if not missing and response.status_code == 200:
    print("✓ All checks passed! Your bot should work.")
    print()
    print("To run the bot:")
    print("  1. Start actions server: rasa run actions")
    print("  2. In another terminal: rasa shell")
elif response.status_code == 403:
    print("⚠️  API returns 403 (Forbidden)")
    print()
    print("SOLUTION:")
    print("  1. Get a FREE API key: https://www.weatherapi.com/signup.aspx")
    print("  2. Set it: setx WEATHERAPI_KEY \"your_new_key\"  (Windows)")
    print("          or export WEATHERAPI_KEY=\"your_new_key\"  (Linux/Mac)")
    print("  3. Restart your terminal")
    print("  4. Run this test again")
else:
    print("⚠️  Some issues detected. Review the errors above.")
print()
