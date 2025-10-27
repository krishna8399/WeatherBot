"""
Custom Rasa actions for WeatherBot.

This module contains:
- _suggest_outfit: Pure helper that maps weather conditions to outfit advice.
- ActionWeatherOutfit: Fetches weather and summarizes conditions (kept for backward compatibility).
- ActionWeatherDetail: Answers a specific requested detail (humidity, wind, uv, etc.).
- ActionWeatherBrief: Returns a short weather summary, and answers yes/no style condition questions.
- ActionProvideOutfit: Uses existing weather data (or fetches) to provide outfit suggestions.

Key concepts:
- Each action class extends rasa_sdk.Action and implements name() and run().
- run() returns a list of events (e.g., SlotSet) and uses dispatcher.utter_message(...) to respond.
- We store a dictionary from WeatherAPI in the slot "weather_data" for reuse by other actions.

External dependency:
- WEATHERAPI_KEY must be available in the environment for live API calls (WeatherAPI.com).
"""

from typing import Any, Text, Dict, List, Optional
import os
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


def _suggest_outfit(temp_c: float, description: str) -> str:
	"""
	Return an outfit suggestion based on temperature and a free-text description.

	The logic gives precedence to precipitation-related descriptions (rain/snow), then
	falls back to temperature bands in Celsius.
	"""
	# Normalize description to lowercase for simple substring checks
	desc = description.lower()

	# 1) Precipitation/conditions take precedence over temperature bands
	if any(k in desc for k in ("rain", "drizzle", "thunderstorm")):
		return "It looks wet — bring an umbrella and wear a waterproof jacket."
	if "snow" in desc:
		return "Snowy — wear a warm coat, insulated boots and consider layers."

	# 2) Temperature-based suggestions. Ranges are inclusive of lower bound and
	# exclusive of the upper bound (except the last), e.g., 18 <= temp < 26.
	if temp_c >= 26:
		return "Hot — light clothing, sunglasses and sunscreen are recommended."
	if 18 <= temp_c < 26:
		return "Nice weather — a t-shirt or light shirt is fine; take a light jacket just in case."
	if 10 <= temp_c < 18:
		return "A bit cool — wear a sweater or layered clothing with a jacket."
	if 0 <= temp_c < 10:
		return "Cold — wear a coat, hat and gloves."
	return "Freezing — wear a heavy winter coat, thermal layers and warm boots."


class ActionWeatherOutfit(Action):
	"""Fetch current weather for a city and suggest an outfit.

	Note: The flow now uses ActionWeatherBrief + ActionProvideOutfit, but we keep this
	action for backward compatibility and simple single-step answers.
	"""

	def name(self) -> Text:
		return "action_weather_outfit"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		# Retrieve the location from a slot first
		location = tracker.get_slot("location")
		if not location:
			# Fall back to extracting the entity directly from the last user message
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			# If still no location, ask a follow-up question via a response template
			dispatcher.utter_message(response="utter_ask_location")
			return []
		# WeatherAPI key is read from the environment. This avoids hardcoding secrets.
		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []
		# Build the WeatherAPI current conditions endpoint URL
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			# Perform the HTTP request with a short timeout
			resp = requests.get(url, timeout=8)
			data = resp.json()
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			# WeatherAPI places relevant fields under "current"
			current = data.get("current", {})
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			desc = f"{condition}, {temp_c}°C"
			# Send a concise weather summary
			dispatcher.utter_message(text=f"Current weather in {location}: {desc}")
			# Persist the raw "current" dictionary for follow-up actions
			return [SlotSet("weather_data", current)]
		except Exception as e:
			# Network or parsing errors are reported to the user
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherDetail(Action):
	"""Provide a specific weather detail (humidity, wind, UV, etc.) for a city.

	Flow:
	1) Ensure we have a location and a requested detail (slot/entity).
	2) Fetch current conditions from WeatherAPI.
	3) Map the requested detail to a concrete API field and unit.
	4) Respond with the formatted value and store weather_data for reuse.
	"""

	def name(self) -> Text:
		return "action_weather_detail"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		# Try to read slots first (location/detail may be set by NLU or a prior step)
		location = tracker.get_slot("location")
		detail = tracker.get_slot("weather_detail")
		if not location:
			# If location slot is missing, extract from latest message entities
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			# Ask the user to provide a location
			dispatcher.utter_message(response="utter_ask_location")
			return []
		if not detail:
			# Similarly extract a detail if the slot is empty
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "weather_detail":
					detail = e.get("value")
					break
		if not detail:
			# Provide guidance for acceptable detail keywords
			dispatcher.utter_message(text="Which weather detail do you want? (e.g. humidity, wind, UV, pressure)")
			return []
		# Get API key from environment
		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []
		# Build WeatherAPI call for current conditions
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			# Issue HTTP request
			resp = requests.get(url, timeout=8)
			data = resp.json()
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			# Map user detail to API field
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
			# Support fuzzy matching: if the requested detail contains a known key
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
			# Respond with the value and unit
			dispatcher.utter_message(text=f"{detail.title()} in {location}: {value}{unit}")
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			# Save weather data for later use (e.g., outfit suggestion)
			return [SlotSet("weather_data", current)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherBrief(Action):
	"""Fetch current weather for a city and report a brief summary (no outfit).

	If the user's utterance contains keywords like rain/snow/sunny/cloud, the bot
	answers directly to that condition with relevant context; otherwise, it returns
	a generic concise summary.
	"""

	def name(self) -> Text:
		return "action_weather_brief"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		# Prefer a previously stored location in the slot
		location = tracker.get_slot("location")
		if not location:
			# Attempt to extract the location entity from the latest user message
			entities = tracker.latest_message.get("entities", [])
			for e in entities:
				if e.get("entity") == "location":
					location = e.get("value")
					break
		if not location:
			# Ask the user to provide a location if not known yet
			dispatcher.utter_message(response="utter_ask_location")
			return []
		# WeatherAPI.com key is required
		weatherapi_key = os.environ.get("WEATHERAPI_KEY")
		if not weatherapi_key:
			dispatcher.utter_message(text="WeatherAPI key not set.")
			return []
		# Build request URL for current conditions
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			# Make the HTTP request
			resp = requests.get(url, timeout=8)
			data = resp.json()
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			
			# Check if user asked about rain/snow/specific condition.
			# This provides a direct yes/no style answer when appropriate.
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
				# General weather report
				desc = f"{condition}, {temp_c}°C"
				dispatcher.utter_message(text=f"Current weather in {location}: {desc}")
			
			# Store current weather for reuse by ActionProvideOutfit
			return [SlotSet("weather_data", current)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []
class ActionProvideOutfit(Action):
	"""Provide outfit suggestion based on stored weather_data or by fetching current weather.

	If the slot "weather_data" is present, we reuse it; otherwise we fetch current weather
	for the known location to avoid asking the user again.
	"""

	def name(self) -> Text:
		return "action_provide_outfit"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		# Read weather_data if available (set by ActionWeatherBrief/Detail)
		current = tracker.get_slot("weather_data") or {}
		location = tracker.get_slot("location")
		# If no weather_data, try to fetch briefly
		if not current:
			weatherapi_key = os.environ.get("WEATHERAPI_KEY")
			if not (weatherapi_key and location):
				dispatcher.utter_message(text="I don't have recent weather to base an outfit on. Ask for the weather first.")
				return []
			# Fetch current weather quickly to base the outfit suggestion on
			url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
			try:
				resp = requests.get(url, timeout=8)
				data = resp.json()
				if "error" in data:
					dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
					return []
				current = data.get("current", {})
			except Exception as e:
				dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
				return []
		# Compose the suggestion using temperature and textual condition
		temp_c = (current or {}).get("temp_c")
		condition = (current or {}).get("condition", {}).get("text", "")
		outfit = _suggest_outfit(temp_c, condition)
		dispatcher.utter_message(text=f"Outfit suggestion: {outfit}")
		return []
		# NOTE: There is intentionally no return of SlotSet here since outfit advice does
		# not modify state. Legacy, unreachable code that mixed WeatherAPI and OWM flows
		# has been left out to keep behavior clear and maintainable.


if __name__ == "__main__":
	# Quick local test (not executed in Rasa) - keep for developer convenience
	pass
