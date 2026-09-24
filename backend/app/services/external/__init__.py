from app.services.external.data_service import ExternalDataService
from app.services.external.opensky_client import fetch_live_flights, fetch_all_states
from app.services.external.weather_client import fetch_current_weather, fetch_weather_forecast
from app.services.external.aviationstack_client import (
    fetch_live_flights as aviationstack_fetch,
    get_bts_delay_statistics,
)

__all__ = [
    "ExternalDataService",
    "fetch_live_flights",
    "fetch_all_states",
    "fetch_current_weather",
    "fetch_weather_forecast",
    "aviationstack_fetch",
    "get_bts_delay_statistics",
]
