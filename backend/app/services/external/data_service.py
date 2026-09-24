"""
External Data Service — Unified orchestration layer
Coordinates OpenSky, OpenWeatherMap, AviationStack, and BTS data
into a single enriched data pipeline for the optimizer.
"""
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List

from app.core.config import settings
from app.services.external.opensky_client import (
    fetch_live_flights as opensky_flights,
    fetch_live_departures as opensky_departures,
    fetch_all_states,
    US_MAJOR_AIRPORTS,
)
from app.services.external.weather_client import (
    fetch_current_weather,
    fetch_weather_forecast,
    AIRPORT_COORDS,
)
from app.services.external.aviationstack_client import (
    fetch_live_flights as aviationstack_flights,
    get_bts_delay_statistics,
    AIRLINES,
    TOP_ROUTES,
)

logger = logging.getLogger("airport_optimizer")


class ExternalDataService:
    """
    Unified service for fetching and enriching data from multiple external sources.
    Merges OpenSky tracking + AviationStack status + OpenWeatherMap weather.
    """

    @staticmethod
    async def get_live_airport_snapshot(airport_iata: str = "ATL") -> Dict[str, Any]:
        """
        Full airport snapshot: live flights + weather + BTS stats.
        All sources run concurrently for performance.
        """
        # Map IATA to ICAO for OpenSky
        iata_to_icao = {v: k for k, v in US_MAJOR_AIRPORTS.items()}
        airport_icao = iata_to_icao.get(airport_iata.upper(), f"K{airport_iata.upper()}")
        api_key_ow = getattr(settings, "OPENWEATHER_API_KEY", None)
        api_key_as = getattr(settings, "AVIATIONSTACK_API_KEY", None)

        # Run all fetches concurrently
        arrivals_task = opensky_flights(airport_icao)
        departures_task = opensky_departures(airport_icao)
        weather_task = fetch_current_weather(airport_iata, api_key_ow)
        forecast_task = fetch_weather_forecast(airport_iata, api_key_ow)
        avstack_task = aviationstack_flights(airport_iata, "arrival", api_key_as, limit=15)

        (
            opensky_arr,
            opensky_dep,
            weather,
            forecast_data,
            avstack_data,
        ) = await asyncio.gather(
            arrivals_task, departures_task, weather_task, forecast_task, avstack_task,
            return_exceptions=True,
        )

        # Handle exceptions gracefully
        if isinstance(opensky_arr, Exception):
            opensky_arr = []
        if isinstance(opensky_dep, Exception):
            opensky_dep = []
        if isinstance(weather, Exception):
            weather = {"airport": airport_iata, "source": "error"}
        if isinstance(forecast_data, Exception):
            forecast_data = {"airport": airport_iata, "forecast": []}
        if isinstance(avstack_data, Exception):
            avstack_data = []

        # Enrich AviationStack with weather delay factor
        weather_delay_factor = ExternalDataService._compute_weather_delay_factor(weather)
        for flight in avstack_data:
            flight["weather_delay_factor"] = weather_delay_factor
            flight["weather_condition"] = weather.get("weather_condition", "Clear")

        return {
            "airport": airport_iata,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "weather": weather,
            "forecast": forecast_data.get("forecast", []) if isinstance(forecast_data, dict) else [],
            "live_arrivals_opensky": opensky_arr if isinstance(opensky_arr, list) else [],
            "live_departures_opensky": opensky_dep if isinstance(opensky_dep, list) else [],
            "flight_status_aviationstack": avstack_data if isinstance(avstack_data, list) else [],
            "weather_delay_factor": weather_delay_factor,
            "data_sources": ["opensky", "openweathermap", "aviationstack", "bts_synthetic"],
        }

    @staticmethod
    async def get_weather_for_airports(airport_codes: List[str]) -> Dict[str, Any]:
        """Fetch weather for multiple airports concurrently."""
        api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
        tasks = [fetch_current_weather(code, api_key) for code in airport_codes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return {
            code: (result if not isinstance(result, Exception) else {"error": str(result)})
            for code, result in zip(airport_codes, results)
        }

    @staticmethod
    async def get_synthetic_flight_batch(airport: str = "ATL", count: int = 50) -> List[Dict[str, Any]]:
        """Generate BTS-realistic synthetic flight batch for an airport."""
        api_key = getattr(settings, "AVIATIONSTACK_API_KEY", None)
        arrivals = await aviationstack_flights(airport, "arrival", api_key, count // 2)
        departures = await aviationstack_flights(airport, "departure", api_key, count // 2)
        return arrivals + departures

    @staticmethod
    def get_bts_statistics() -> Dict[str, Any]:
        """Return real BTS delay statistics."""
        return get_bts_delay_statistics()

    @staticmethod
    def get_supported_airports() -> List[Dict[str, Any]]:
        """Return list of supported airports with metadata."""
        from app.services.external.weather_client import AIRPORT_WEATHER_PROFILE
        airports = []
        for iata, icao in US_MAJOR_AIRPORTS.items():
            coords = AIRPORT_COORDS.get(iata, (0, 0))
            profile = AIRPORT_WEATHER_PROFILE.get(iata, {})
            airports.append({
                "iata": iata,
                "icao": icao,
                "latitude": coords[0],
                "longitude": coords[1],
                "weather_profile": profile,
                "has_weather_data": iata in AIRPORT_COORDS,
            })
        return sorted(airports, key=lambda x: x["iata"])

    @staticmethod
    def get_airlines() -> List[Dict[str, str]]:
        """Return list of tracked airlines."""
        from app.services.external.aviationstack_client import AIRLINE_DELAY_RATES
        return [
            {
                "iata": code,
                "name": name,
                "delay_rate_pct": round(AIRLINE_DELAY_RATES.get(code, 0.20) * 100, 1),
            }
            for code, name in AIRLINES.items()
        ]

    @staticmethod
    def get_top_routes() -> List[Dict[str, str]]:
        """Return top domestic routes by traffic volume."""
        return [{"origin": o, "destination": d} for o, d in TOP_ROUTES]

    @staticmethod
    def _compute_weather_delay_factor(weather: Dict[str, Any]) -> float:
        """
        Compute a weather delay multiplier (1.0 = no impact, 3.0 = severe).
        Based on FAA Weather Delay Impact studies.
        """
        if not isinstance(weather, dict):
            return 1.0

        factor = 1.0
        condition = weather.get("weather_condition", "Clear").lower()
        wind = weather.get("wind_speed_kmh", 0) or 0
        visibility = weather.get("visibility_km", 10) or 10
        precip = weather.get("precipitation_mm", 0) or 0

        # Condition-based modifiers
        condition_modifiers = {
            "thunderstorm": 2.5, "blizzard": 3.0, "heavy rain": 2.0,
            "snow": 2.2, "fog": 1.8, "moderate rain": 1.5,
            "light rain": 1.2, "overcast": 1.05, "broken clouds": 1.02,
        }
        for key, mod in condition_modifiers.items():
            if key in condition:
                factor *= mod
                break

        # Wind speed modifier (FAA: >25 knots = ATC restriction likely)
        if wind > 75:     # 75 km/h ≈ 40 knots
            factor *= 1.5
        elif wind > 55:   # 55 km/h ≈ 30 knots
            factor *= 1.3
        elif wind > 40:   # 40 km/h ≈ 22 knots
            factor *= 1.1

        # Low visibility modifier
        if visibility < 0.8:     # < 800m = ILS CAT III required
            factor *= 2.0
        elif visibility < 1.6:   # < 1 mile
            factor *= 1.6
        elif visibility < 5.0:
            factor *= 1.2

        # Precipitation intensity
        if precip > 20:
            factor *= 1.4
        elif precip > 10:
            factor *= 1.2
        elif precip > 2:
            factor *= 1.1

        return round(min(factor, 5.0), 2)  # cap at 5x
