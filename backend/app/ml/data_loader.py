import os
import random
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from typing import Optional, Tuple


def generate_synthetic_airport_dataset(
    num_samples: int = 5000,
    start_date: datetime = datetime(2026, 8, 1, 0, 0, 0),
    seed: int = 42
) -> pd.DataFrame:
    """
    Generates a realistic, statistically grounded synthetic airport operational dataset.
    Note: Clearly labeled as synthetic data for demonstration, evaluation, and research.
    """
    random.seed(seed)
    np.random.seed(seed)

    airlines = ["Air India", "IndiGo", "Vistara", "SpiceJet", "Emirates", "British Airways", "Lufthansa", "Delta Air Lines"]
    aircraft_types = ["A320", "A321", "B737", "B777", "B787", "A350"]
    origins = ["DEL", "BOM", "BLR", "HYD", "MAA", "DXB", "LHR", "FRA", "JFK", "SIN"]
    destinations = ["BOM", "DEL", "BLR", "CCU", "GOI", "DXB", "LHR", "DOH", "NRT"]
    terminals = ["T1", "T2", "T3"]
    runways = ["RWY-09L", "RWY-09R", "RWY-27L", "RWY-27R", "RWY-28"]
    weather_conditions = ["Clear", "Rain", "Fog", "Thunderstorm", "Overcast"]

    rows = []
    current_time = start_date

    for i in range(num_samples):
        # Time progression with clusters
        flight_offset = random.randint(1, 15)
        current_time += timedelta(minutes=flight_offset)
        
        airline = random.choices(airlines, weights=[0.25, 0.35, 0.15, 0.10, 0.05, 0.04, 0.03, 0.03])[0]
        aircraft = random.choices(aircraft_types, weights=[0.40, 0.25, 0.20, 0.07, 0.05, 0.03])[0]
        
        origin = random.choice(origins)
        dest = random.choice([d for d in destinations if d != origin])
        terminal = random.choice(terminals)
        runway = random.choice(runways)
        
        sched_arrival = current_time
        turnaround = random.choice([35.0, 45.0, 50.0, 60.0, 75.0, 90.0])
        sched_departure = sched_arrival + timedelta(minutes=turnaround + random.randint(15, 45))
        
        hour = sched_arrival.hour
        is_peak = 1 if hour in [7, 8, 9, 17, 18, 19, 20] else 0
        
        # Weather generation
        temp = round(float(np.random.normal(28, 6)), 1)
        wind = round(max(2.0, float(np.random.normal(12 if is_peak else 8, 5))), 1)
        visibility = round(max(0.5, float(np.random.normal(8.0, 2.5))), 1)
        precipitation = round(float(np.random.exponential(1.2)) if random.random() < 0.25 else 0.0, 1)
        
        if visibility < 2.0:
            weather_cond = "Fog"
        elif precipitation > 5.0:
            weather_cond = "Thunderstorm"
        elif precipitation > 0.0:
            weather_cond = "Rain"
        elif temp > 32 and random.random() < 0.3:
            weather_cond = "Overcast"
        else:
            weather_cond = "Clear"
            
        # Congestion metrics
        active_flights = int(np.clip(np.random.poisson(45 if is_peak else 22), 5, 80))
        flights_per_hour = int(np.clip(active_flights * 0.7 + np.random.normal(0, 3), 4, 60))
        arrivals_per_hour = int(flights_per_hour * 0.55)
        departures_per_hour = flights_per_hour - arrivals_per_hour

        # Base nominal taxi times
        nominal_taxi_in = float(np.random.normal(12.0, 2.0))
        nominal_taxi_out = float(np.random.normal(16.0, 3.0))

        # True Delay Generation (Physics-inspired statistical model)
        # Delay = base_delay + congestion_impact + weather_impact + airline_efficiency + noise
        weather_delay = 0.0
        if weather_cond == "Thunderstorm":
            weather_delay += random.uniform(20.0, 45.0)
        elif weather_cond == "Fog":
            weather_delay += random.uniform(15.0, 35.0)
        elif weather_cond == "Rain":
            weather_delay += random.uniform(5.0, 18.0)
            
        if visibility < 3.0:
            weather_delay += (3.0 - visibility) * 5.0
        if wind > 20.0:
            weather_delay += (wind - 20.0) * 1.5

        congestion_delay = (active_flights / 50.0) ** 1.8 * 14.0 if active_flights > 25 else (active_flights * 0.2)
        peak_delay = 8.5 if is_peak else 1.0
        
        airline_delay_bias = {
            "Air India": 3.0,
            "IndiGo": -1.5,
            "Vistara": -1.0,
            "SpiceJet": 4.0,
            "Emirates": -0.5,
            "British Airways": 1.0,
            "Lufthansa": 0.5,
            "Delta Air Lines": 0.0
        }.get(airline, 0.0)

        random_noise = float(np.random.normal(0, 4.0))
        
        # Primary regression target: taxi_delay_minutes
        total_delay = max(0.0, float(congestion_delay + weather_delay + peak_delay + airline_delay_bias + random_noise))
        total_delay = round(total_delay, 1)

        actual_arrival = sched_arrival + timedelta(minutes=total_delay)
        actual_departure = sched_departure + timedelta(minutes=total_delay + random.randint(0, 10))

        flight_num = f"{airline[:2].upper()}{random.randint(100, 999)}"

        rows.append({
            "flight_number": flight_num,
            "airline": airline,
            "aircraft_type": aircraft,
            "origin": origin,
            "destination": dest,
            "terminal": terminal,
            "scheduled_arrival": sched_arrival.isoformat(),
            "estimated_arrival": (sched_arrival + timedelta(minutes=total_delay * 0.8)).isoformat(),
            "actual_arrival": actual_arrival.isoformat(),
            "scheduled_departure": sched_departure.isoformat(),
            "estimated_departure": (sched_departure + timedelta(minutes=total_delay * 0.8)).isoformat(),
            "actual_departure": actual_departure.isoformat(),
            "runway": runway,
            "taxi_in_minutes": round(nominal_taxi_in + (total_delay * 0.4), 1),
            "taxi_out_minutes": round(nominal_taxi_out + (total_delay * 0.6), 1),
            "turnaround_minutes": turnaround,
            "status": "Delayed" if total_delay > 15 else "Scheduled",
            "temperature": temp,
            "wind_speed": wind,
            "visibility": visibility,
            "precipitation": precipitation,
            "weather_condition": weather_cond,
            "active_flights": active_flights,
            "flights_per_hour": flights_per_hour,
            "arrivals_per_hour": arrivals_per_hour,
            "departures_per_hour": departures_per_hour,
            "taxi_delay_minutes": total_delay  # Primary Target
        })

    return pd.DataFrame(rows)


def load_dataset(csv_path: Optional[str] = None) -> pd.DataFrame:
    """
    Loads dataset from CSV path or generates synthetic dataset if path is not found.
    """
    if csv_path and os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return generate_synthetic_airport_dataset(num_samples=5000)
