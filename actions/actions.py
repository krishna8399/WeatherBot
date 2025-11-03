"""
Actions for WeatherBot (cleaned and hardened).

Improved behaviors:
- HTTP requests use a small retry/backoff helper and an in-memory cache to reduce API calls.
- Location normalization is applied.
- Better None-handling for missing temperature values.
"""

from typing import Any, Text, Dict, List, Optional
import os
import requests
import time
from functools import lru_cache

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


def _http_get_with_retries(url: str, timeout: int = 8, retries: int = 2, backoff: float = 0.6):
	"""Perform a simple GET with retries and exponential backoff.

	Keeps this file dependency-free (no tenacity). For production you may swap in
	a more robust library.
	"""
	last_exc = None
	for i in range(retries + 1):
		try:
			resp = requests.get(url, timeout=timeout)
			resp.raise_for_status()
			return resp
		except Exception as e:
			last_exc = e
			time.sleep(backoff * (2 ** i))
	raise last_exc


def _cache_key(location: str, ttl_seconds: int = 600) -> str:
	bucket = int(time.time() // ttl_seconds)
	return f"{location.lower().strip()}::{bucket}"


@lru_cache(maxsize=256)
def _fetch_weather_cached(cache_key: str, url: str) -> Dict[str, Any]:
	resp = _http_get_with_retries(url)
	return resp.json()


def _suggest_outfit(temp_c: Optional[float], description: str) -> str:
	"""Return outfit suggestion. Handles None temp gracefully using description.

	Temperature-based rules take precedence for extreme values (freezing/hot),
	but precipitation words still influence mid-range temperatures.
	"""
	desc = (description or "").lower()

	# If temperature not available, fall back to condition-based rules
	if temp_c is None:
		if any(k in desc for k in ("rain", "drizzle", "thunderstorm")):
			return "It looks wet — bring an umbrella and wear a waterproof jacket."
		if "snow" in desc:
			return "Snowy — wear a warm coat, insulated boots and consider layers."
		return "I don't have the exact temperature, but check the current conditions and dress accordingly — layers are a good default."

	try:
		temp = float(temp_c)
	except Exception:
		return "I couldn't read the temperature — wear layers and check local forecasts."

	# Temperature-first logic for extremes
	if temp < 0:
		return "Freezing — wear a heavy winter coat, thermal layers and warm boots."
	if temp >= 26:
		return "Hot — light clothing, sunglasses and sunscreen are recommended."

	# Mid-range temperatures: allow precipitation to override
	if any(k in desc for k in ("rain", "drizzle", "thunderstorm")):
		return "It looks wet — bring an umbrella and wear a waterproof jacket."
	if "snow" in desc:
		return "Snowy — wear a warm coat, insulated boots and consider layers."

	if 18 <= temp < 26:
		return "Nice weather — a t-shirt or light shirt is fine; take a light jacket just in case."
	if 10 <= temp < 18:
		return "A bit cool — wear a sweater or layered clothing with a jacket."
	if 0 <= temp < 10:
		return "Cold — wear a coat, hat and gloves."
	return "Freezing — wear a heavy winter coat, thermal layers and warm boots."


class ActionWeatherOutfit(Action):
	def name(self) -> Text:
		return "action_weather_outfit"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		location = tracker.get_slot("location")
		if not location:
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			dispatcher.utter_message(response="utter_ask_location")
			return []

		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []

		location = location.strip()
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			cache_key = _cache_key(location)
			data = _fetch_weather_cached(cache_key, url)
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			dispatcher.utter_message(text=f"Current weather in {location}: {condition}, {temp_c}°C")
			return [SlotSet("weather_data", current), SlotSet("location", location)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherDetail(Action):
	def name(self) -> Text:
		return "action_weather_detail"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		location = tracker.get_slot("location")
		detail = tracker.get_slot("weather_detail")
		if not location:
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			dispatcher.utter_message(response="utter_ask_location")
			return []
		if not detail:
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "weather_detail":
					detail = e.get("value")
					break
		if not detail:
			dispatcher.utter_message(text="Which weather detail do you want? (e.g. humidity, wind, UV, pressure)")
			return []

		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []

		location = location.strip()
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			cache_key = _cache_key(location)
			data = _fetch_weather_cached(cache_key, url)
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			detail_map = {
				"humidity": ("humidity", "%"),
				"wind": ("wind_kph", "kph"),
				"wind_mph": ("wind_mph", "mph"),
				"wind_kph": ("wind_kph", "kph"),
				"uv": ("uv", ""),
				"pressure": ("pressure_mb", "mb"),
				"cloud": ("cloud", "%"),
				"feelslike": ("feelslike_c", "°C"),
				"gust": ("gust_kph", "kph"),
				"precipitation": ("precip_mm", "mm"),
				"temperature": ("temp_c", "°C"),
			}
			key = None
			unit = ""
			for k, v in detail_map.items():
				if k in detail.lower():
					key, unit = v
					break
			if not key:
				dispatcher.utter_message(text=f"Sorry, I can't provide '{detail}'. Try: humidity, wind, UV, pressure, cloud, feelslike, gust, precipitation, temperature.")
				return []
			value = current.get(key)
			if value is None:
				dispatcher.utter_message(text=f"{detail.title()} data not available for {location}.")
				return []
			dispatcher.utter_message(text=f"{detail.title()} in {location}: {value}{unit}")
			return [SlotSet("weather_data", current), SlotSet("location", location)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherBrief(Action):
	def name(self) -> Text:
		return "action_weather_brief"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		location = tracker.get_slot("location")
		if not location:
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			dispatcher.utter_message(response="utter_ask_location")
			return []

		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []

		location = location.strip()
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			cache_key = _cache_key(location)
			data = _fetch_weather_cached(cache_key, url)
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			user_text = tracker.latest_message.get("text", "").lower()
			if "rain" in user_text:
				precip_mm = current.get("precip_mm", 0)
				if precip_mm > 0 or "rain" in condition.lower():
					dispatcher.utter_message(text=f"Yes, it's currently raining in {location}. {condition}, {temp_c}°C. Precipitation: {precip_mm}mm.")
				else:
					dispatcher.utter_message(text=f"No, it's not raining in {location} right now. {condition}, {temp_c}°C.")
			elif "snow" in user_text:
				if "snow" in condition.lower():
					dispatcher.utter_message(text=f"Yes, it's snowing in {location}. {condition}, {temp_c}°C.")
				else:
					dispatcher.utter_message(text=f"No, it's not snowing in {location}. {condition}, {temp_c}°C.")
			elif "sunny" in user_text or "sun" in user_text:
				if "sunny" in condition.lower() or "clear" in condition.lower():
					dispatcher.utter_message(text=f"Yes, it's sunny in {location}. {condition}, {temp_c}°C.")
				else:
					dispatcher.utter_message(text=f"Not very sunny in {location} right now. {condition}, {temp_c}°C.")
			elif "cloud" in user_text:
				cloud_pct = current.get("cloud", 0)
				dispatcher.utter_message(text=f"Cloud cover in {location}: {cloud_pct}%. {condition}, {temp_c}°C.")
			else:
				dispatcher.utter_message(text=f"Current weather in {location}: {condition}, {temp_c}°C")
			return [SlotSet("weather_data", current), SlotSet("location", location)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionProvideOutfit(Action):
	def name(self) -> Text:
		return "action_provide_outfit"

	def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
		location = tracker.get_slot("location")
		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		
		if not (weatherapi_key and location):
			dispatcher.utter_message(text="I don't have a location to base an outfit on. Ask for the weather in a city first.")
			return []
		
		# Always fetch fresh weather for the current location to avoid stale data
		location = location.strip()
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			cache_key = _cache_key(location)
			data = _fetch_weather_cached(cache_key, url)
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []

		temp_c = (current or {}).get("temp_c")
		condition = (current or {}).get("condition", {}).get("text", "")
		outfit = _suggest_outfit(temp_c, condition)
		dispatcher.utter_message(text=f"Outfit suggestion for {location}: {outfit}")
		return []


if __name__ == "__main__":
	pass
