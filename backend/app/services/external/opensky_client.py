"""
OpenSky Network API Client
Free, no API key required. Provides real-time ADS-B flight tracking data.
Docs: https://openskynetwork.github.io/opensky-api/rest.html
"""
import httpx
import asyncio
import logging
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

logger = logging.getLogger("airport_optimizer")

OPENSKY_BASE_URL = "https://opensky-network.org/api"

# Major US airport ICAO codes for filtering
US_MAJOR_AIRPORTS = {
    "KATL": "ATL", "KLAX": "LAX", "KORD": "ORD", "KDFW": "DFW",
    "KDEN": "DEN", "KJFK": "JFK", "KSFO": "SFO", "KLAS": "LAS",
    "KMCO": "MCO", "KSEA": "SEA", "KBOS": "BOS", "KPHX": "PHX",
    "KEWR": "EWR", "KMSP": "MSP", "KPHL": "PHL", "KLGA": "LGA",
    "KDTW": "DTW", "KBWI": "BWI", "KIAD": "IAD", "KMDW": "MDW",
    "KHOU": "HOU", "KIAH": "IAH", "KMIA": "MIA", "KCLT": "CLT",
}

ICAO_TO_IATA = {v: k for k, v in US_MAJOR_AIRPORTS.items()}


async def fetch_live_flights(
    airport_icao: str = "KATL",
    timeout_seconds: int = 15
) -> List[Dict[str, Any]]:
    """
    Fetch live flights arriving/departing a given airport from OpenSky Network.
    Falls back to empty list on failure (network or rate-limit).
    """
    url = f"{OPENSKY_BASE_URL}/flights/arrival"
    now = int(datetime.now(timezone.utc).timestamp())
    begin = now - 7200  # last 2 hours

    params = {
        "airport": airport_icao,
        "begin": begin,
        "end": now,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"OpenSky: fetched {len(data)} arrivals for {airport_icao}")
                return _normalize_opensky(data, airport_icao)
            else:
                logger.warning(f"OpenSky API returned {resp.status_code} for {airport_icao}")
                return []
    except Exception as e:
        logger.warning(f"OpenSky fetch failed for {airport_icao}: {e}")
        return []


async def fetch_live_departures(
    airport_icao: str = "KATL",
    timeout_seconds: int = 15
) -> List[Dict[str, Any]]:
    """Fetch live departures from OpenSky Network."""
    url = f"{OPENSKY_BASE_URL}/flights/departure"
    now = int(datetime.now(timezone.utc).timestamp())
    begin = now - 7200

    params = {
        "airport": airport_icao,
        "begin": begin,
        "end": now,
    }

    try:
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                logger.info(f"OpenSky: fetched {len(data)} departures for {airport_icao}")
                return _normalize_opensky(data, airport_icao, is_arrival=False)
            else:
                logger.warning(f"OpenSky departures returned {resp.status_code}")
                return []
    except Exception as e:
        logger.warning(f"OpenSky departures fetch failed: {e}")
        return []


async def fetch_all_states(bbox: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """
    Fetch all current aircraft states (live positions).
    bbox: (min_lat, max_lat, min_lon, max_lon) — optional bounding box
    """
    url = f"{OPENSKY_BASE_URL}/states/all"
    params = {}
    if bbox:
        params["lamin"], params["lamax"], params["lomin"], params["lomax"] = bbox

    try:
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                states = data.get("states", []) or []
                return [_normalize_state(s) for s in states[:200]]  # cap at 200
            else:
                logger.warning(f"OpenSky states returned {resp.status_code}")
                return []
    except Exception as e:
        logger.warning(f"OpenSky states fetch failed: {e}")
        return []


def _normalize_opensky(raw: list, airport_icao: str, is_arrival: bool = True) -> List[Dict]:
    """Normalize OpenSky flight records to our schema."""
    results = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        icao24 = item.get("icao24", "")
        callsign = (item.get("callsign") or "").strip()
        estDep = item.get("estDepartureAirport") or ""
        estArr = item.get("estArrivalAirport") or ""

        results.append({
            "icao24": icao24,
            "callsign": callsign,
            "flight_number": callsign[:8] if callsign else f"UNK-{icao24[:4]}",
            "origin_icao": estDep,
            "dest_icao": estArr,
            "origin": US_MAJOR_AIRPORTS.get(estDep, estDep[:3] if estDep else "UNK"),
            "destination": US_MAJOR_AIRPORTS.get(estArr, estArr[:3] if estArr else "UNK"),
            "first_seen": item.get("firstSeen"),
            "last_seen": item.get("lastSeen"),
            "source": "opensky",
            "is_arrival": is_arrival,
        })
    return results


def _normalize_state(s: list) -> Dict:
    """Normalize OpenSky state vector to a readable dict."""
    keys = [
        "icao24", "callsign", "origin_country", "time_position",
        "last_contact", "longitude", "latitude", "baro_altitude",
        "on_ground", "velocity", "true_track", "vertical_rate",
        "sensors", "geo_altitude", "squawk", "spi", "position_source"
    ]
    result = {}
    for i, k in enumerate(keys):
        result[k] = s[i] if i < len(s) else None
    result["callsign"] = (result.get("callsign") or "").strip()
    return result
