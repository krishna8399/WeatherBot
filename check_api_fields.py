import os
import requests
import json

key = os.environ.get('WEATHERAPI_KEY')
resp = requests.get(f'http://api.weatherapi.com/v1/current.json?key={key}&q=Berlin&aqi=no')
data = resp.json()['current']

fields = ['temp_c', 'condition', 'humidity', 'wind_kph', 'wind_mph', 'uv', 
          'pressure_mb', 'cloud', 'feelslike_c', 'gust_kph', 'precip_mm']

print('Checking required fields:')
for f in fields:
    if f == 'condition':
        status = 'OK' if 'condition' in data else 'MISSING'
    else:
        status = 'OK' if f in data else 'MISSING'
    print(f'  {f}: {status}')

print('\nSample values:')
print(f'  Temperature: {data.get("temp_c")}°C')
print(f'  Condition: {data.get("condition", {}).get("text")}')
print(f'  Humidity: {data.get("humidity")}%')
print(f'  Wind: {data.get("wind_kph")} kph')
print(f'  UV: {data.get("uv")}')
print(f'  Precipitation: {data.get("precip_mm")} mm')
