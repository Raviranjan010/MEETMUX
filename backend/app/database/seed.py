import os
from datetime import datetime, timedelta
import random
from sqlalchemy.orm import Session
from app.database.database import Base, engine, SessionLocal
from app.models.flight import Flight
from app.models.gate import Gate
from app.models.weather import Weather
from app.models.prediction import DelayPrediction
from app.models.optimization import OptimizationRun, GateAssignment
from app.services.prediction_service import PredictionService
from app.services.optimization_service import OptimizationService
from app.schemas.optimization import OptimizationRequest
from app.core.logging import logger


def seed_database(db: Session = None):
    """
    Seeds database with a rich demo scenario:
    - 12 realistic Gates across 3 terminals (T1, T2, T3)
    - 30 diverse Flights (Domestic & International, various aircraft types, tight turnaround windows)
    - Realistic weather observations
    - Pre-computed ML predictions for all flights
    - Baseline Gate Assignment Optimization run for instant dashboard visualization.
    """
    logger.info("Dropping and recreating database tables for fresh seed...")
    Base.metadata.create_all(bind=engine)

    close_db_after = False
    if db is None:
        db = SessionLocal()
        close_db_after = True

    try:
        # Clear existing rows
        db.query(GateAssignment).delete()
        db.query(OptimizationRun).delete()
        db.query(DelayPrediction).delete()
        db.query(Flight).delete()
        db.query(Gate).delete()
        db.query(Weather).delete()
        db.commit()

        # 1. Seed Gates
        gates_data = [
            # Terminal 1 - Domestic Narrow-body
            {"gate_number": "A01", "terminal": "T1", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
            {"gate_number": "A02", "terminal": "T1", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
            {"gate_number": "A03", "terminal": "T1", "gate_type": "Contact", "supported_aircraft_types": "A320,B737", "is_international": False, "is_available": True},
            {"gate_number": "A04", "terminal": "T1", "gate_type": "Remote", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
            
            # Terminal 2 - Mixed Domestic & Medium Haul
            {"gate_number": "B01", "terminal": "T2", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787", "is_international": False, "is_available": True},
            {"gate_number": "B02", "terminal": "T2", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777", "is_international": False, "is_available": True},
            {"gate_number": "B03", "terminal": "T2", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},
            {"gate_number": "B04", "terminal": "T2", "gate_type": "Remote", "supported_aircraft_types": "A320,A321,B737", "is_international": False, "is_available": True},

            # Terminal 3 - International & Wide-body Hub
            {"gate_number": "C01", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
            {"gate_number": "C02", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
            {"gate_number": "C03", "terminal": "T3", "gate_type": "Contact", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
            {"gate_number": "C04", "terminal": "T3", "gate_type": "Remote", "supported_aircraft_types": "A320,A321,B737,B787,B777,A350", "is_international": True, "is_available": True},
        ]

        gate_objects = [Gate(**g) for g in gates_data]
        db.add_all(gate_objects)
        db.commit()
        logger.info(f"Seeded {len(gate_objects)} airport gates.")

        # 2. Seed Weather
        weather_objects = [
            Weather(timestamp=datetime.utcnow(), temperature=29.2, wind_speed=11.5, visibility=7.8, precipitation=0.0, weather_condition="Clear"),
            Weather(timestamp=datetime.utcnow() - timedelta(hours=1), temperature=28.4, wind_speed=13.0, visibility=6.5, precipitation=0.4, weather_condition="Rain"),
            Weather(timestamp=datetime.utcnow() - timedelta(hours=2), temperature=27.5, wind_speed=15.0, visibility=5.0, precipitation=1.2, weather_condition="Rain"),
        ]
        db.add_all(weather_objects)
        db.commit()

        # 3. Seed Realistic Flights
        now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
        
        flights_catalog = [
            # T1 flights
            ("AI101", "Air India", "A320", "DEL", "BOM", "T1", 0, 60, "RWY-09L", 45),
            ("6E202", "IndiGo", "A320", "BLR", "DEL", "T1", 15, 75, "RWY-09L", 40),
            ("SG303", "SpiceJet", "B737", "DEL", "HYD", "T1", 30, 95, "RWY-09R", 45),
            ("6E404", "IndiGo", "A321", "MAA", "DEL", "T1", 45, 110, "RWY-09L", 50),
            ("AI105", "Air India", "A320", "DEL", "CCU", "T1", 70, 130, "RWY-09R", 45),
            ("6E606", "IndiGo", "A320", "GOI", "DEL", "T1", 85, 145, "RWY-09L", 40),
            ("SG707", "SpiceJet", "B737", "DEL", "PNQ", "T1", 100, 160, "RWY-09R", 45),
            ("6E808", "IndiGo", "A321", "AMD", "DEL", "T1", 120, 180, "RWY-09L", 45),
            ("AI109", "Air India", "A320", "DEL", "COK", "T1", 140, 200, "RWY-09R", 45),
            ("6E910", "IndiGo", "A320", "JAI", "DEL", "T1", 155, 215, "RWY-09L", 40),

            # T2 flights
            ("UK811", "Vistara", "A320", "DEL", "BOM", "T2", 10, 75, "RWY-09L", 50),
            ("6E212", "IndiGo", "A321", "DEL", "BLR", "T2", 25, 90, "RWY-09R", 45),
            ("UK813", "Vistara", "B787", "DEL", "DXB", "T2", 50, 135, "RWY-27L", 75),
            ("AI114", "Air India", "B777", "DEL", "LHR", "T2", 65, 155, "RWY-27R", 80),
            ("UK815", "Vistara", "A320", "HYD", "DEL", "T2", 80, 140, "RWY-09L", 45),
            ("6E216", "IndiGo", "A320", "BOM", "DEL", "T2", 95, 155, "RWY-09R", 40),
            ("UK817", "Vistara", "A321", "DEL", "MAA", "T2", 115, 180, "RWY-09L", 50),
            ("AI118", "Air India", "B787", "DEL", "SIN", "T2", 135, 220, "RWY-27L", 75),
            ("6E219", "IndiGo", "A320", "CCU", "DEL", "T2", 150, 210, "RWY-09R", 40),
            ("UK820", "Vistara", "A320", "DEL", "BLR", "T2", 170, 230, "RWY-09L", 45),

            # T3 flights (International & High Capacity)
            ("EK511", "Emirates", "B777", "DXB", "DEL", "T3", 5, 105, "RWY-27L", 90),
            ("BA142", "British Airways", "B787", "LHR", "DEL", "T3", 20, 115, "RWY-27R", 85),
            ("LH760", "Lufthansa", "A350", "FRA", "DEL", "T3", 40, 140, "RWY-27L", 90),
            ("DL024", "Delta Air Lines", "A350", "JFK", "DEL", "T3", 60, 160, "RWY-27R", 90),
            ("AI125", "Air India", "B787", "DEL", "SFO", "T3", 75, 170, "RWY-27L", 85),
            ("EK513", "Emirates", "A350", "DXB", "DEL", "T3", 90, 185, "RWY-27R", 85),
            ("BA144", "British Airways", "B777", "LHR", "DEL", "T3", 110, 205, "RWY-27L", 85),
            ("LH762", "Lufthansa", "B787", "FRA", "DEL", "T3", 130, 220, "RWY-27R", 80),
            ("AI129", "Air India", "A321", "DOH", "DEL", "T3", 145, 215, "RWY-09L", 60),
            ("EK515", "Emirates", "B777", "DEL", "DXB", "T3", 165, 255, "RWY-27L", 85),
        ]

        flight_objects = []
        for (fnum, airl, ac, orig, dest, term, arr_min, dep_min, rwy, turn) in flights_catalog:
            s_arr = now + timedelta(minutes=arr_min)
            s_dep = now + timedelta(minutes=dep_min)
            flight_objects.append(Flight(
                flight_number=fnum,
                airline=airl,
                aircraft_type=ac,
                origin=orig,
                destination=dest,
                terminal=term,
                scheduled_arrival=s_arr,
                scheduled_departure=s_dep,
                estimated_arrival=s_arr,
                estimated_departure=s_dep,
                runway=rwy,
                taxi_in_minutes=12.0,
                taxi_out_minutes=15.0,
                turnaround_minutes=float(turn),
                status="Scheduled"
            ))

        db.add_all(flight_objects)
        db.commit()
        logger.info(f"Seeded {len(flight_objects)} operational flights.")

        # 4. Generate Machine Learning Delay Predictions for all flights
        logger.info("Computing ML delay predictions for seeded flights...")
        PredictionService.predict_batch_flights(db)

        # 5. Run Initial Gate Assignment Optimization
        logger.info("Running baseline MILP Gate Optimization for seed data...")
        OptimizationService.run_optimization(db, OptimizationRequest(
            solver="ortools",
            time_limit_seconds=30
        ))

        logger.info("Database seeding successfully completed!")
        print("\n" + "="*60)
        print("  AIRPORT DATABASE SEEDING COMPLETED")
        print(f"  - 12 Airport Gates (T1, T2, T3)")
        print(f"  - {len(flight_objects)} Scheduled Flights")
        print(f"  - ML Predictions Generated")
        print(f"  - Baseline Optimization Solved & Visualized")
        print("="*60 + "\n")

    finally:
        if close_db_after:
            db.close()


if __name__ == "__main__":
    seed_database()
