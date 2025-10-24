from typing import Any, Text, Dict, List, Optional
import os
import requests

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


def _suggest_outfit(temp_c: float, description: str) -> str:
	desc = description.lower()
	# Rainy/snowy conditions take precedence
	if any(k in desc for k in ("rain", "drizzle", "thunderstorm")):
		return "It looks wet — bring an umbrella and wear a waterproof jacket."
	if "snow" in desc:
		return "Snowy — wear a warm coat, insulated boots and consider layers."

	# Temperature based suggestions (temp_c expected)
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
	"""Fetch current weather for a city and suggest an outfit."""

	def name(self) -> Text:
		return "action_weather_outfit"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
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
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
			resp = requests.get(url, timeout=8)
			data = resp.json()
			if "error" in data:
				dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
				return []
			current = data.get("current", {})
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			desc = f"{condition}, {temp_c}°C"
			dispatcher.utter_message(text=f"Current weather in {location}: {desc}")
			return [SlotSet("weather_data", current)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherDetail(Action):
	"""Provide specific weather detail (humidity, wind, UV, etc.) for a city."""

	def name(self) -> Text:
		return "action_weather_detail"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
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
		url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
		try:
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
			temp_c = current.get("temp_c")
			condition = current.get("condition", {}).get("text", "")
			# Save weather data for later use
			return [SlotSet("weather_data", current)]
		except Exception as e:
			dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
			return []


class ActionWeatherBrief(Action):
    """Fetch current weather for a city and report a brief summary (no outfit)."""

    def name(self) -> Text:
        return "action_weather_brief"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
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
        url = f"http://api.weatherapi.com/v1/current.json?key={weatherapi_key}&q={location}&aqi=no"
        try:
            resp = requests.get(url, timeout=8)
            data = resp.json()
            if "error" in data:
                dispatcher.utter_message(text=f"WeatherAPI error: {data['error'].get('message','Unknown error')}")
                return []
            current = data.get("current", {})
            temp_c = current.get("temp_c")
            condition = current.get("condition", {}).get("text", "")
            
            # Check if user asked about rain/snow/specific condition
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
            
            return [SlotSet("weather_data", current)]
        except Exception as e:
            dispatcher.utter_message(text=f"Failed to fetch weather: {e}")
            return []
class ActionProvideOutfit(Action):
	"""Provide outfit suggestion based on stored weather_data or by fetching current weather."""

	def name(self) -> Text:
		return "action_provide_outfit"

	def run(
		self,
		dispatcher: CollectingDispatcher,
		tracker: Tracker,
		domain: Dict[Text, Any],
	) -> List[Dict[Text, Any]]:
		current = tracker.get_slot("weather_data") or {}
		location = tracker.get_slot("location")
		# If no weather_data, try to fetch briefly
		if not current:
			weatherapi_key = os.environ.get("WEATHERAPI_KEY")
			if not (weatherapi_key and location):
				dispatcher.utter_message(text="I don't have recent weather to base an outfit on. Ask for the weather first.")
				return []
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
		temp_c = (current or {}).get("temp_c")
		condition = (current or {}).get("condition", {}).get("text", "")
		outfit = _suggest_outfit(temp_c, condition)
		dispatcher.utter_message(text=f"Outfit suggestion: {outfit}")
		return []

		if not (weatherapi_key or openweather_key):
			dispatcher.utter_message(response="utter_no_api_key")
			return []

		data = None
		resp = None

		# Prefer WeatherAPI if available (user provided key from weatherapi.com)
		if weatherapi_key:
			try:
				params = {"key": weatherapi_key, "q": location, "aqi": "no"}
				resp = requests.get(
					"http://api.weatherapi.com/v1/current.json", params=params, timeout=8
				)
				data = resp.json()
			except Exception as e:
				dispatcher.utter_message(text=f"Sorry, I couldn't reach the weather service: {e}")
				return []

			if resp.status_code != 200:
				# WeatherAPI returns JSON with 'error' object for errors
				msg = data.get("error", {}).get("message", "unknown error")
				dispatcher.utter_message(text=f"I couldn't fetch the weather for {location} (error {resp.status_code}: {msg}).")
				return []

			# Parse WeatherAPI response
			temp_c = data.get("current", {}).get("temp_c")
			weather_desc = data.get("current", {}).get("condition", {}).get("text", "")

		else:
			# Fallback to OpenWeatherMap
			try:
				params = {"q": location, "appid": openweather_key, "units": "metric"}
				resp = requests.get(
					"http://api.openweathermap.org/data/2.5/weather", params=params, timeout=8
				)
				data = resp.json()
			except Exception as e:
				dispatcher.utter_message(text=f"Sorry, I couldn't reach the weather service: {e}")
				return []

			if resp.status_code != 200:
				msg = data.get("message", "unknown error")
				dispatcher.utter_message(text=f"I couldn't fetch the weather for {location} (error {resp.status_code}: {msg}).")
				return []

			temp_c = data.get("main", {}).get("temp")
			weather_desc = "".join([w.get("description", "") for w in data.get("weather", [])])
		# Compose reply
		try:
			temp_text = f"{temp_c:.1f}°C"
		except Exception:
			temp_text = f"{temp_c}°C"

		outfit = _suggest_outfit(float(temp_c), weather_desc)

		text = f"Current weather in {location}: {weather_desc}. Temperature: {temp_text}. {outfit}"
		dispatcher.utter_message(text=text)

		# Remember location for follow-ups
		return [SlotSet("location", location)]


if __name__ == "__main__":
	# Quick local test (not executed in Rasa) - keep for developer convenience
	pass
