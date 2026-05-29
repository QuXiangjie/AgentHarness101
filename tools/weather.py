# Shared weather tool: one source of truth imported by all four harnesses.
# Pure logic + the JSON tool schema. No SDK / framework deps -- just requests --
# so the raw-HTTP and SDK harnesses can import it without pulling in langchain.
import requests

# JSON tool schema for the raw-HTTP and Claude-SDK harnesses.
GET_WEATHER_TOOL = {
    "name": "get_weather",
    "description": "Get the current weather for a city.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string"}},
        "required": ["city"],
    },
}

def get_weather(city):
    """Get the current weather for a city."""
    # City name -> coordinates (Open-Meteo geocoding, no API key needed).
    results = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={"name": city, "count": 1},
    ).json().get("results", [])
    if not results:
        return f"Couldn't find a city called {city!r}."
    place = results[0]

    # Coordinates -> current temperature (Open-Meteo forecast).
    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={"latitude": place["latitude"], "longitude": place["longitude"], "current": "temperature_2m"},
    ).json()
    return f"It's {weather['current']['temperature_2m']}°C in {place['name']}."
