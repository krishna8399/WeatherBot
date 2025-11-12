#!/bin/bash

echo "============================================"
echo "WeatherBot API Key Setup (Linux/Mac)"
echo "============================================"
echo ""
echo "For evaluation purposes, use this key:"
echo "309d537f8f694e30a7283845252310"
echo ""

read -p "Enter your WeatherAPI key (or press Enter to use default): " API_KEY

if [ -z "$API_KEY" ]; then
    API_KEY="309d537f8f694e30a7283845252310"
    echo "Using default evaluation key..."
fi

echo ""
echo "Setting environment variable..."

# Detect shell
if [ -n "$ZSH_VERSION" ]; then
    SHELL_RC="$HOME/.zshrc"
elif [ -n "$BASH_VERSION" ]; then
    SHELL_RC="$HOME/.bashrc"
else
    SHELL_RC="$HOME/.profile"
fi

# Add to shell config if not already present
if ! grep -q "WEATHERAPI_KEY" "$SHELL_RC" 2>/dev/null; then
    echo "" >> "$SHELL_RC"
    echo "# WeatherBot API Key" >> "$SHELL_RC"
    echo "export WEATHERAPI_KEY=\"$API_KEY\"" >> "$SHELL_RC"
    echo "Added to $SHELL_RC"
else
    echo "Already exists in $SHELL_RC (you may need to update manually)"
fi

# Set for current session
export WEATHERAPI_KEY="$API_KEY"

echo ""
echo "============================================"
echo "Setup Complete!"
echo "============================================"
echo ""
echo "The API key has been added to: $SHELL_RC"
echo ""
echo "To use in NEW terminals, run:"
echo "  source $SHELL_RC"
echo ""
echo "To verify, run:"
echo "  echo \$WEATHERAPI_KEY"
echo ""

echo "Testing API connection..."
python3 -c "import os, requests; key=os.environ.get('WEATHERAPI_KEY', '$API_KEY'); r=requests.get(f'http://api.weatherapi.com/v1/current.json?key={key}&q=London'); print('✓ API Working!' if r.status_code==200 else f'✗ API Error: {r.status_code}')" 2>/dev/null || echo "Note: Python test skipped (requests module may not be installed yet)"

echo ""
