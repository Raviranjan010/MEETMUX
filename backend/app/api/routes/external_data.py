"""
External Data API Routes
Exposes OpenSky, OpenWeatherMap, AviationStack, and BTS data via REST endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Query, HTTPException, status
from pydantic import BaseModel

from app.services.external.data_service import ExternalDataService

router = APIRouter(prefix="/external", tags=["External Data"])


class AirportSnapshotResponse(BaseModel):
    airport: str
    timestamp: str
    weather: dict
    forecast: list
    live_arrivals_opensky: list
    live_departures_opensky: list
    flight_status_aviationstack: list
    weather_delay_factor: float
    data_sources: list

    model_config = {"arbitrary_types_allowed": True}


@router.get(
    "/airport/{airport_iata}/snapshot",
    summary="Full live airport snapshot: flights + weather + delay data",
    response_model=AirportSnapshotResponse,
)
async def get_airport_snapshot(
    airport_iata: str,
    include_opensky: bool = Query(True, description="Include OpenSky live flight tracking"),
):
    """
    Fetches a full real-time snapshot for an airport by merging:
    - **OpenSky Network**: Live ADS-B flight arrivals and departures
    - **OpenWeatherMap**: Current weather and 48h forecast
    - **AviationStack**: Real-time flight status with delay info
    
    All sources run concurrently. Falls back gracefully when sources are unavailable.
    """
    iata = airport_iata.upper()
    snapshot = await ExternalDataService.get_live_airport_snapshot(iata)
    return AirportSnapshotResponse(**snapshot)


@router.get(
    "/weather/{airport_iata}",
    summary="Current weather conditions for an airport",
)
async def get_airport_weather(airport_iata: str):
    """Get current weather for a specific airport (real or realistic mock)."""
    from app.services.external.weather_client import fetch_current_weather
    from app.core.config import settings
    api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
    return await fetch_current_weather(airport_iata.upper(), api_key)


@router.get(
    "/weather/{airport_iata}/forecast",
    summary="48-hour weather forecast for an airport",
)
async def get_airport_forecast(airport_iata: str):
    """Get 48-hour weather forecast with 3-hour resolution."""
    from app.services.external.weather_client import fetch_weather_forecast
    from app.core.config import settings
    api_key = getattr(settings, "OPENWEATHER_API_KEY", None)
    return await fetch_weather_forecast(airport_iata.upper(), api_key)


@router.get(
    "/weather/multi",
    summary="Simultaneous weather fetch for multiple airports",
)
async def get_multi_airport_weather(
    airports: str = Query(
        "ATL,ORD,JFK,LAX,DFW",
        description="Comma-separated IATA codes (max 10)"
    )
):
    """Fetch weather for up to 10 airports simultaneously."""
    codes = [c.strip().upper() for c in airports.split(",")][:10]
    return await ExternalDataService.get_weather_for_airports(codes)


@router.get(
    "/flights/live",
    summary="Live flight status from AviationStack (BTS-synthetic fallback)",
)
async def get_live_flights(
    airport: str = Query("ATL", description="Airport IATA code"),
    flight_type: str = Query("arrival", description="'arrival' or 'departure'"),
    count: int = Query(20, ge=1, le=50, description="Number of flights"),
):
    """
    Real-time flight data. Uses AviationStack API if key is configured,
    otherwise generates BTS-statistical synthetic flights.
    """
    from app.services.external.aviationstack_client import fetch_live_flights
    from app.core.config import settings
    api_key = getattr(settings, "AVIATIONSTACK_API_KEY", None)
    return await fetch_live_flights(airport.upper(), flight_type, api_key, count)


@router.get(
    "/flights/opensky/{airport_icao}",
    summary="Live ADS-B flight tracking from OpenSky Network (free, no key)",
)
async def get_opensky_flights(
    airport_icao: str,
    include_departures: bool = Query(False, description="Include departures as well"),
):
    """
    Real-time flight positions from OpenSky Network.
    Completely free, no API key required. Data may be up to 60s delayed.
    """
    from app.services.external.opensky_client import fetch_live_flights, fetch_live_departures
    arrivals = await fetch_live_flights(airport_icao.upper())
    if include_departures:
        departures = await fetch_live_departures(airport_icao.upper())
        return {"arrivals": arrivals, "departures": departures, "source": "opensky"}
    return {"arrivals": arrivals, "source": "opensky"}


@router.get(
    "/bts/statistics",
    summary="Real BTS Bureau of Transportation Statistics delay data (2023)",
)
def get_bts_statistics():
    """
    Returns real U.S. Bureau of Transportation Statistics (BTS) flight delay data.
    Source: BTS T-100 Domestic Segment Data, 2023 annual report.
    Includes on-time performance, delay causes, worst/best airports.
    """
    return ExternalDataService.get_bts_statistics()


@router.get(
    "/airports",
    summary="List all supported airports with metadata",
)
def get_supported_airports():
    """List all airports with IATA/ICAO codes, coordinates, and weather profiles."""
    return {"airports": ExternalDataService.get_supported_airports()}


@router.get(
    "/airlines",
    summary="List airlines with BTS historical delay rates",
)
def get_airlines():
    """Returns tracked airlines with their 2023 BTS historical on-time performance."""
    return {"airlines": ExternalDataService.get_airlines()}


@router.get(
    "/routes/top",
    summary="Top US domestic routes by traffic volume",
)
def get_top_routes():
    """Returns the top 40 highest-traffic domestic city-pair routes (BTS T-100 data)."""
    return {"routes": ExternalDataService.get_top_routes()}


@router.get(
    "/data-sources",
    summary="Status of all integrated data sources",
)
async def get_data_sources_status():
    """Check the status and capabilities of all integrated external data sources."""
    from app.core.config import settings
    has_owm = bool(getattr(settings, "OPENWEATHER_API_KEY", ""))
    has_avstack = bool(getattr(settings, "AVIATIONSTACK_API_KEY", ""))

    return {
        "sources": [
            {
                "name": "OpenSky Network",
                "status": "active",
                "requires_key": False,
                "configured": True,
                "tier": "free",
                "data_type": "Real-time ADS-B flight tracking",
                "url": "https://opensky-network.org/api",
                "rate_limit": "100 req/day (anonymous)",
            },
            {
                "name": "OpenWeatherMap",
                "status": "active" if has_owm else "mock_fallback",
                "requires_key": True,
                "configured": has_owm,
                "tier": "free (60 calls/min)",
                "data_type": "Current weather + 5-day forecast",
                "url": "https://openweathermap.org/api",
                "setup": "Set OPENWEATHER_API_KEY in backend/.env",
            },
            {
                "name": "AviationStack",
                "status": "active" if has_avstack else "synthetic_fallback",
                "requires_key": True,
                "configured": has_avstack,
                "tier": "free (100 req/month)",
                "data_type": "Real-time flight status & delays",
                "url": "https://aviationstack.com/",
                "setup": "Set AVIATIONSTACK_API_KEY in backend/.env",
            },
            {
                "name": "BTS T-100 Dataset",
                "status": "active",
                "requires_key": False,
                "configured": True,
                "tier": "public_data",
                "data_type": "Historical US flight delay statistics (2023)",
                "url": "https://www.transtats.bts.gov/",
            },
        ],
        "total_configured": sum([True, has_owm, has_avstack, True]),
        "total_sources": 4,
    }
