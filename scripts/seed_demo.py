import sys
import os
import random
from datetime import datetime, timedelta, timezone

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

from app.core.db import SessionLocal, engine
from app.models import (
    Airport,
    Terminal,
    Runway,
    Gate,
    Aircraft,
    Flight,
    WeatherRecord,
    Prediction,
    OptimizationRun,
    GateAssignment,
    Scenario,
    Alert,
    CascadeEvent,
    AuditRecord,
    SystemConfig,
    RunwayStatus,
    GateType,
    AircraftSizeClass,
    RouteType,
    GateEligibleRouteType,
    GateStatus,
    WeatherCondition,
)


def seed_demo_data(reset: bool = False):
    random.seed(42)
    db = SessionLocal()

    try:
        if reset:
            print("--- Resetting Database Tables ---")
            db.query(GateAssignment).delete()
            db.query(OptimizationRun).delete()
            db.query(Alert).delete()
            db.query(CascadeEvent).delete()
            db.query(Scenario).delete()
            db.query(Prediction).delete()
            db.query(AuditRecord).delete()
            db.query(Flight).delete()
            db.query(Gate).delete()
            db.query(Runway).delete()
            db.query(Terminal).delete()
            db.query(WeatherRecord).delete()
            db.query(Aircraft).delete()
            db.query(Airport).delete()
            db.query(SystemConfig).delete()
            db.commit()

        print("--- Seeding RunwayOptX Demo Dataset (Seed 42) ---")

        # 1. System Config (Single row)
        existing_config = db.query(SystemConfig).first()
        if not existing_config:
            config = SystemConfig(
                risk_low_max_minutes=5.0,
                risk_medium_max_minutes=15.0,
                turnaround_buffer_minutes=15,
                optimizer_timeout_seconds=60,
                optimizer_weight_delay_cost=1.0,
                optimizer_weight_conflict_cost=50.0,
                optimizer_weight_reassignment_cost=5.0,
                optimizer_weight_taxi_distance=0.1,
                optimizer_weight_remote_stand=10.0,
                cascade_max_depth=5,
            )
            db.add(config)
            db.commit()
            print("SystemConfig seeded.")

        # 2. Airport
        airport = db.query(Airport).filter_by(code="DFW").first()
        if not airport:
            airport = Airport(
                code="DFW",
                name="RunwayOptX International Airport",
                timezone="UTC",
            )
            db.add(airport)
            db.commit()
            print("Airport DFW created.")

        # 3. Terminals (3 terminals)
        terminals = {}
        for t_code, t_name in [("T1", "Terminal 1"), ("T2", "Terminal 2"), ("T3", "Terminal 3")]:
            term = db.query(Terminal).filter_by(airport_id=airport.id, code=t_code).first()
            if not term:
                term = Terminal(airport_id=airport.id, code=t_code, name=t_name)
                db.add(term)
                db.commit()
                print(f"Terminal {t_code} created.")
            terminals[t_code] = term

        # 4. Runways (2 runways per REQUIREMENTS NFR-1)
        runway_specs = [
            ("RWY-1", RunwayStatus.ACTIVE, 12.0),
            ("RWY-2", RunwayStatus.ACTIVE, 15.0),
        ]
        runways = {}
        for r_code, r_status, r_taxi in runway_specs:
            rwy = db.query(Runway).filter_by(airport_id=airport.id, code=r_code).first()
            if not rwy:
                rwy = Runway(
                    airport_id=airport.id,
                    code=r_code,
                    status=r_status,
                    taxi_base_minutes=r_taxi,
                )
                db.add(rwy)
                db.commit()
                print(f"Runway {r_code} created.")
            runways[r_code] = rwy

        # 5. Gates (Exactly 30 gates: 10 per terminal)
        gate_types_cycle = [GateType.JETBRIDGE] * 8 + [GateType.REMOTE] * 2
        sizes_cycle = [AircraftSizeClass.MEDIUM, AircraftSizeClass.LARGE, AircraftSizeClass.SMALL,
                       AircraftSizeClass.MEDIUM, AircraftSizeClass.LARGE, AircraftSizeClass.MEDIUM,
                       AircraftSizeClass.SMALL, AircraftSizeClass.LARGE, AircraftSizeClass.MEDIUM,
                       AircraftSizeClass.SMALL]
        routes_cycle = [GateEligibleRouteType.DOMESTIC, GateEligibleRouteType.BOTH, GateEligibleRouteType.DOMESTIC,
                        GateEligibleRouteType.INTERNATIONAL, GateEligibleRouteType.BOTH, GateEligibleRouteType.DOMESTIC,
                        GateEligibleRouteType.BOTH, GateEligibleRouteType.INTERNATIONAL, GateEligibleRouteType.DOMESTIC,
                        GateEligibleRouteType.BOTH]
        
        gate_count = 0
        all_gates = []
        for t_idx, (t_code, term) in enumerate(terminals.items(), start=1):
            for g_num in range(1, 11):
                g_code = f"G{t_idx}{g_num:02d}"
                gate = db.query(Gate).filter_by(terminal_id=term.id, code=g_code).first()
                if not gate:
                    idx = g_num - 1
                    dist = 250.0 + (t_idx * 100.0) + (g_num * 35.0)
                    gate = Gate(
                        terminal_id=term.id,
                        code=g_code,
                        gate_type=gate_types_cycle[idx],
                        max_aircraft_size=sizes_cycle[idx],
                        eligible_route_types=routes_cycle[idx],
                        status=GateStatus.AVAILABLE,
                        taxi_distance_meters=dist,
                    )
                    db.add(gate)
                    db.commit()
                all_gates.append(gate)
                gate_count += 1
        print(f"Total gates ensured: {len(all_gates)} (Target: 30)")

        # 6. Aircraft Fleet (Multiple types and size classes)
        aircraft_specs = [
            ("N101AA", "A320", AircraftSizeClass.MEDIUM),
            ("N102AA", "A320", AircraftSizeClass.MEDIUM),
            ("N103AA", "B738", AircraftSizeClass.MEDIUM),
            ("N104AA", "B738", AircraftSizeClass.MEDIUM),
            ("N201DL", "A359", AircraftSizeClass.LARGE),
            ("N202DL", "B77W", AircraftSizeClass.LARGE),
            ("N203DL", "A320", AircraftSizeClass.MEDIUM),
            ("N204DL", "CRJ9", AircraftSizeClass.SMALL),
            ("N301UA", "B77W", AircraftSizeClass.LARGE),
            ("N302UA", "B738", AircraftSizeClass.MEDIUM),
            ("N303UA", "CRJ9", AircraftSizeClass.SMALL),
            ("N304UA", "E190", AircraftSizeClass.SMALL),
            ("G-XLEA", "A359", AircraftSizeClass.LARGE),
            ("G-ZBKA", "B77W", AircraftSizeClass.LARGE),
            ("D-AIZF", "A320", AircraftSizeClass.MEDIUM),
            ("D-ABYA", "B77W", AircraftSizeClass.LARGE),
            ("F-HEPG", "A320", AircraftSizeClass.MEDIUM),
            ("F-GZND", "B77W", AircraftSizeClass.LARGE),
        ]
        aircraft_list = []
        for reg, type_code, size_class in aircraft_specs:
            ac = db.query(Aircraft).filter_by(registration=reg).first()
            if not ac:
                ac = Aircraft(registration=reg, type_code=type_code, size_class=size_class)
                db.add(ac)
                db.commit()
            aircraft_list.append(ac)
        print(f"Total aircraft fleet ensured: {len(aircraft_list)}")

        # 7. Weather Record
        weather = db.query(WeatherRecord).filter_by(airport_id=airport.id).first()
        if not weather:
            weather = WeatherRecord(
                airport_id=airport.id,
                recorded_at=datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc),
                condition=WeatherCondition.CLEAR,
                wind_speed_kt=8.5,
                visibility_m=10000.0,
            )
            db.add(weather)
            db.commit()
            print("Baseline weather record created.")

        # 8. Flights (Exactly 100 flights per REQUIREMENTS NFR-1)
        existing_flight_count = db.query(Flight).count()
        if existing_flight_count < 100:
            # We seed deterministic flights
            airlines = ["AA", "DL", "UA", "BA", "LH", "AF"]
            destinations_dom = ["ORD", "ATL", "LAX", "DEN", "MIA", "SFO", "JFK", "SEA"]
            destinations_int = ["LHR", "FRA", "CDG", "HND", "ICN", "GRU"]

            base_time = datetime(2026, 10, 1, 6, 0, tzinfo=timezone.utc)
            rwy_keys = list(runways.keys())

            flights_to_create = 100 - existing_flight_count
            print(f"Generating {flights_to_create} flights to reach exactly 100...")

            for i in range(flights_to_create):
                idx = existing_flight_count + i + 1
                airline = airlines[idx % len(airlines)]
                ac = aircraft_list[idx % len(aircraft_list)]
                is_intl = (airline in ["BA", "LH", "AF"]) or (idx % 4 == 0)
                route_type = RouteType.INTERNATIONAL if is_intl else RouteType.DOMESTIC
                dest = random.choice(destinations_int) if is_intl else random.choice(destinations_dom)
                orig = "DFW" if idx % 2 == 0 else dest
                dest = dest if idx % 2 == 0 else "DFW"

                # Stagger flights between 06:00 and 22:00
                minute_offset = int((idx / 100.0) * (16 * 60))
                arr_time = base_time + timedelta(minutes=minute_offset)
                # Turnaround 45 - 90 minutes
                turnaround = random.choice([45, 50, 60, 75, 90])
                dep_time = arr_time + timedelta(minutes=turnaround)

                rwy_code = rwy_keys[idx % len(rwy_keys)]
                flight_num = f"{airline}{100 + idx}"

                flight = Flight(
                    flight_number=flight_num,
                    airline=airline,
                    aircraft_id=ac.id,
                    route_type=route_type,
                    origin=orig,
                    destination=dest,
                    runway_id=runways[rwy_code].id,
                    scheduled_arrival=arr_time,
                    scheduled_departure=dep_time,
                    is_synthetic=True,
                )
                db.add(flight)

            db.commit()
            print(f"Total flights in DB now: {db.query(Flight).count()}")
        else:
            print(f"100 flights already exist (count: {existing_flight_count}). Idempotent skip.")

        # Final assertion check
        final_flights = db.query(Flight).count()
        final_gates = db.query(Gate).count()
        final_runways = db.query(Runway).count()
        print(f"\nSeed Complete Verification:")
        print(f" - Flights: {final_flights} (Expected: 100)")
        print(f" - Gates:   {final_gates} (Expected: 30)")
        print(f" - Runways: {final_runways} (Expected: 2)")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_data()
