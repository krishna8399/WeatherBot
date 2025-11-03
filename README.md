# WeatherBot

This repository contains a Rasa-based WeatherBot.

Quickstart (PowerShell):

```powershell
# create and activate your Python venv or conda env (example uses conda)
conda create -n weather_env python=3.10 -y; conda activate weather_env
pip install -r requirements.txt
# set your WeatherAPI key:
$env:WEATHERAPI_KEY = "<your_key_here>"
# train and run
rasa train
rasa run actions &
rasa shell
```

See `run.ps1` for shortcuts.
