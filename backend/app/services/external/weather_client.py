"""
OpenWeatherMap API Client
Free tier: 60 calls/min, current weather + forecasts.
Sign up at: https://openweathermap.org/api
Set OPENWEATHER_API_KEY in your .env file.

Without a key, this client returns realistic mock weather data
generated from historical airport climate statistics.
"""
import httpx
import random
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any

logger = logging.getLogger("airport_optimizer")

OWM_BASE_URL = "https://api.openweathermap.org/data/2.5"

# Approximate lat/lon for major US airports
AIRPORT_COORDS = {
    "ATL": (33.6407, -84.4277), "LAX": (33.9425, -118.4081),
    "ORD": (41.9742, -87.9073), "DFW": (32.8998, -97.0403),
    "DEN": (39.8561, -104.6737), "JFK": (40.6413, -73.7781),
    "SFO": (37.6213, -122.3790), "LAS": (36.0840, -115.1537),
    "MCO": (28.4312, -81.3081), "SEA": (47.4502, -122.3088),
    "BOS": (42.3656, -71.0096), "PHX": (33.4373, -112.0078),
    "EWR": (40.6895, -74.1745), "MSP": (44.8848, -93.2223),
    "MIA": (25.7959, -80.2870), "CLT": (35.2144, -80.9473),
    "IAH": (29.9902, -95.3368), "DTW": (42.2162, -83.3554),
}

# Seasonal mock weather parameters by airport (realistic historical means)
AIRPORT_WEATHER_PROFILE = {
    "ATL": {"summer_temp": 30, "winter_temp": 8, "rain_prob": 0.35},
    "LAX": {"summer_temp": 25, "winter_temp": 15, "rain_prob": 0.12},
    "ORD": {"summer_temp": 27, "winter_temp": -3, "rain_prob": 0.40},
    "DFW": {"summer_temp": 35, "winter_temp": 10, "rain_prob": 0.30},
    "DEN": {"summer_temp": 28, "winter_temp": 0, "rain_prob": 0.25},
    "JFK": {"summer_temp": 26, "winter_temp": 2, "rain_prob": 0.38},
    "SFO": {"summer_temp": 18, "winter_temp": 11, "rain_prob": 0.22},
    "LAS": {"summer_temp": 40, "winter_temp": 12, "rain_prob": 0.08},
    "MIA": {"summer_temp": 32, "winter_temp": 22, "rain_prob": 0.50},
    "SEA": {"summer_temp": 22, "winter_temp": 7, "rain_prob": 0.55},
    "BOS": {"summer_temp": 25, "winter_temp": -1, "rain_prob": 0.40},
    "PHX": {"summer_temp": 42, "winter_temp": 16, "rain_prob": 0.10},
}

WEATHER_CONDITIONS = [
    ("Clear", 0, 0.0),
    ("Few Clouds", 0, 0.0),
    ("Scattered Clouds", 0, 0.05),
    ("Broken Clouds", 0, 0.10),
    ("Overcast", 0, 0.15),
    ("Light Rain", 2, 0.25),
    ("Moderate Rain", 4, 0.45),
    ("Heavy Rain", 8, 0.80),
    ("Thunderstorm", 12, 1.0),
    ("Snow", 10, 0.70),
    ("Fog", 6, 0.60),
    ("Blizzard", 20, 1.0),
]


async def fetch_current_weather(airport_code: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """
    Fetch current weather for an airport.
    Uses real OWM API if key is provided, else returns mock data.
    """
    if api_key and api_key.lower() not in ("", "none", "your_key_here"):
        return await _fetch_real_weather(airport_code, api_key)
    else:
        return _generate_mock_weather(airport_code)


async def fetch_weather_forecast(airport_code: str, api_key: Optional[str] = None) -> Dict[str, Any]:
    """Fetch 5-day weather forecast (3h intervals) for an airport."""
    if api_key and api_key.lower() not in ("", "none", "your_key_here"):
        return await _fetch_real_forecast(airport_code, api_key)
    else:
        return {"airport": airport_code, "forecast": _generate_forecast_mock(airport_code)}


async def _fetch_real_weather(airport_code: str, api_key: str) -> Dict[str, Any]:
    coords = AIRPORT_COORDS.get(airport_code)
    if not coords:
        return _generate_mock_weather(airport_code)

    lat, lon = coords
    url = f"{OWM_BASE_URL}/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric"}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                return _normalize_owm(data, airport_code)
            else:
                logger.warning(f"OWM API returned {resp.status_code}. Using mock weather.")
                return _generate_mock_weather(airport_code)
    except Exception as e:
        logger.warning(f"OWM fetch failed: {e}. Using mock weather.")
        return _generate_mock_weather(airport_code)


async def _fetch_real_forecast(airport_code: str, api_key: str) -> Dict[str, Any]:
    coords = AIRPORT_COORDS.get(airport_code)
    if not coords:
        return {"airport": airport_code, "forecast": _generate_forecast_mock(airport_code)}

    lat, lon = coords
    url = f"{OWM_BASE_URL}/forecast"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "metric", "cnt": 16}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                items = data.get("list", [])
                return {
                    "airport": airport_code,
                    "forecast": [_normalize_owm_forecast_item(i) for i in items]
                }
            else:
                return {"airport": airport_code, "forecast": _generate_forecast_mock(airport_code)}
    except Exception as e:
        logger.warning(f"OWM forecast failed: {e}")
        return {"airport": airport_code, "forecast": _generate_forecast_mock(airport_code)}


def _normalize_owm(data: dict, airport_code: str) -> Dict[str, Any]:
    """Normalize OWM API response to our weather schema."""
    main = data.get("main", {})
    wind = data.get("wind", {})
    weather_list = data.get("weather", [{}])
    condition = weather_list[0].get("description", "clear sky").title() if weather_list else "Clear"
    visibility_m = data.get("visibility", 10000)
    rain_1h = data.get("rain", {}).get("1h", 0.0)

    return {
        "airport": airport_code,
        "temperature_celsius": round(main.get("temp", 20.0), 1),
        "humidity_percent": main.get("humidity", 50),
        "wind_speed_kmh": round((wind.get("speed", 0) or 0) * 3.6, 1),
        "wind_direction_degrees": wind.get("deg", 0),
        "visibility_km": round(visibility_m / 1000, 1),
        "precipitation_mm": round(rain_1h, 1),
        "weather_condition": condition,
        "cloud_coverage_percent": data.get("clouds", {}).get("all", 0),
        "pressure_hpa": main.get("pressure", 1013),
        "feels_like_celsius": round(main.get("feels_like", main.get("temp", 20)), 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "openweathermap_live",
    }


def _normalize_owm_forecast_item(item: dict) -> Dict[str, Any]:
    main = item.get("main", {})
    wind = item.get("wind", {})
    weather = item.get("weather", [{}])[0]
    rain = item.get("rain", {}).get("3h", 0)
    return {
        "dt": item.get("dt_txt", ""),
        "temp": round(main.get("temp", 20.0), 1),
        "humidity": main.get("humidity", 50),
        "wind_speed_kmh": round((wind.get("speed", 0) or 0) * 3.6, 1),
        "condition": weather.get("description", "").title(),
        "rain_3h_mm": round(rain, 1),
        "clouds": item.get("clouds", {}).get("all", 0),
    }


def _generate_mock_weather(airport_code: str) -> Dict[str, Any]:
    """
    Generate realistic mock weather from historical airport climate data.
    Used when no API key is configured.
    """
    profile = AIRPORT_WEATHER_PROFILE.get(airport_code, {
        "summer_temp": 25, "winter_temp": 5, "rain_prob": 0.30
    })

    month = datetime.now().month
    # Sinusoidal interpolation: summer = Jun-Aug (month 6-8)
    seasonal_factor = 0.5 + 0.5 * (-1 * ((month - 7) / 6) ** 2 + 1)
    temp = profile["winter_temp"] + seasonal_factor * (profile["summer_temp"] - profile["winter_temp"])
    temp += random.gauss(0, 2)

    rain_prob = profile["rain_prob"]
    is_raining = random.random() < rain_prob
    if is_raining:
        weights = [0, 0, 0, 0, 0, 3, 2, 1, 0.5, 0.3, 0.5, 0.1]
        condition, delay_add, precip_intensity = random.choices(WEATHER_CONDITIONS, weights=weights)[0]
        precipitation = round(random.uniform(0.5, 10.0) * precip_intensity, 1) if precip_intensity else 0.0
    else:
        weights = [4, 3, 2, 1.5, 1, 0, 0, 0, 0, 0, 0, 0]
        condition, delay_add, precip_intensity = random.choices(WEATHER_CONDITIONS, weights=weights)[0]
        precipitation = 0.0

    wind_speed = max(0, random.gauss(20, 12))
    visibility = 10.0 if not is_raining else max(0.5, 10 - precipitation * 0.8)

    return {
        "airport": airport_code,
        "temperature_celsius": round(temp, 1),
        "humidity_percent": int(40 + rain_prob * 40 + (20 if is_raining else 0)),
        "wind_speed_kmh": round(wind_speed, 1),
        "wind_direction_degrees": random.randint(0, 359),
        "visibility_km": round(visibility, 1),
        "precipitation_mm": precipitation,
        "weather_condition": condition,
        "cloud_coverage_percent": random.randint(0, 30) if not is_raining else random.randint(60, 100),
        "pressure_hpa": int(random.gauss(1013, 8)),
        "feels_like_celsius": round(temp - wind_speed * 0.05, 1),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "mock_historical_climate",
    }


def _generate_forecast_mock(airport_code: str) -> list:
    """Generate a 16-period (48h) mock forecast."""
    forecast = []
    base_weather = _generate_mock_weather(airport_code)
    temp = base_weather["temperature_celsius"]
    for i in range(16):
        temp += random.gauss(0, 1.2)
        rain = max(0, random.gauss(0, 0.5)) if random.random() < 0.25 else 0
        forecast.append({
            "dt": f"+{i*3}h",
            "temp": round(temp, 1),
            "humidity": base_weather["humidity_percent"] + random.randint(-10, 10),
            "wind_speed_kmh": round(max(0, base_weather["wind_speed_kmh"] + random.gauss(0, 5)), 1),
            "condition": "Light Rain" if rain > 0.5 else "Partly Cloudy" if rain > 0 else "Clear",
            "rain_3h_mm": round(rain, 1),
            "clouds": random.randint(0, 100),
        })
    return forecast
