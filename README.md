# WeatherBot

A conversational AI assistant built with Rasa that provides real-time weather information and personalized outfit recommendations.

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Internet connection

### Setup (2 Easy Steps)

✅ **API Key Already Included!** The WeatherAPI key is hardcoded in the bot for evaluation purposes. No environment setup needed!

**1. Install Dependencies**
```bash
pip install -r requirements.txt
```

**2. Run the Bot**
```bash
rasa run actions &
rasa shell
```

**Note:** The evaluation API key `309d537f8f694e30a7283845252310` is already configured as a fallback in the code.

## 📖 Full Documentation

See **[SETUP_GUIDE.md](SETUP_GUIDE.md)** for detailed instructions, troubleshooting, and alternative setup methods.

## ✅ Verify Installation

Run tests to ensure everything works:
```bash
pytest tests/test_actions.py -v
```

Expected: All 3 tests pass ✅

## 🎯 Features

- Real-time weather data for worldwide locations
- Context-aware conversations (remembers your location)
- Smart outfit recommendations based on weather
- Specific answers for umbrella/sunscreen questions
- UV index and precipitation analysis

## 📦 What's Included

- Complete source code
- Trained Rasa model
- Unit tests (100% pass rate)
- Documentation and presentation
- Docker deployment configuration
- CI/CD pipeline (GitHub Actions)

## 🔧 Troubleshooting

**"API key not set" error?**
→ Run `setup_api_key.bat` (Windows) or `setup_api_key.sh` (Linux/Mac)

**Import errors?**
→ Set PYTHONPATH: `set PYTHONPATH=%CD%` (Windows) or `export PYTHONPATH=$(pwd)` (Linux/Mac)

See [SETUP_GUIDE.md](SETUP_GUIDE.md) for more help.

## 📄 Project Documentation

- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Complete setup instructions
- [PROJECT_ABSTRACT.md](PROJECT_ABSTRACT.md) - Academic project abstract
- [DEPLOYMENT.md](DEPLOYMENT.md) - Docker deployment guide

## 🎓 Academic Use

This project is submitted for academic evaluation. The included API key is for evaluation purposes only and has usage limits.
