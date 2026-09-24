import io
import pandas as pd
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func

from app.models.flight import Flight
from app.models.prediction import DelayPrediction
from app.models.optimization import GateAssignment
from app.schemas.flight import FlightCreate, FlightUpdate, FlightResponse, FlightListResponse, CSVUploadResponse
from app.core.exceptions import FlightNotFoundError, CSVValidationError
from app.core.logging import logger


class FlightService:
    @staticmethod
    def get_flights(
        db: Session,
        page: int = 1,
        page_size: int = 20,
        search: Optional[str] = None,
        airline: Optional[str] = None,
        terminal: Optional[str] = None,
        delay_category: Optional[str] = None,
        status: Optional[str] = None
    ) -> FlightListResponse:
        query = db.query(Flight)

        if search:
            search_clean = f"%{search.strip()}%"
            query = query.filter(
                or_(
                    Flight.flight_number.ilike(search_clean),
                    Flight.airline.ilike(search_clean),
                    Flight.origin.ilike(search_clean),
                    Flight.destination.ilike(search_clean)
                )
            )

        if airline:
            query = query.filter(Flight.airline == airline)
        if terminal:
            query = query.filter(Flight.terminal == terminal)
        if status:
            query = query.filter(Flight.status == status)

        total = query.count()
        total_pages = max(1, (total + page_size - 1) // page_size)
        offset = (page - 1) * page_size

        flights = query.order_by(Flight.scheduled_arrival.asc()).offset(offset).limit(page_size).all()

        # Augment with latest prediction and current gate
        flight_ids = [f.id for f in flights]
        
        # Latest predictions map
        latest_preds = (
            db.query(DelayPrediction)
            .filter(DelayPrediction.flight_id.in_(flight_ids))
            .order_by(desc(DelayPrediction.prediction_timestamp))
            .all()
        )
        pred_map = {}
        for p in latest_preds:
            if p.flight_id not in pred_map:
                pred_map[p.flight_id] = p

        # Latest assignments map
        latest_assigns = (
            db.query(GateAssignment)
            .filter(GateAssignment.flight_id.in_(flight_ids))
            .all()
        )
        assign_map = {a.flight_id: a.gate.gate_number if a.gate else None for a in latest_assigns}

        items = []
        for f in flights:
            p = pred_map.get(f.id)
            g_num = assign_map.get(f.id)
            
            # Apply delay_category filter if requested
            if delay_category and (not p or p.delay_category.lower() != delay_category.lower()):
                continue

            resp_item = FlightResponse(
                id=f.id,
                flight_number=f.flight_number,
                airline=f.airline,
                aircraft_type=f.aircraft_type,
                origin=f.origin,
                destination=f.destination,
                terminal=f.terminal,
                scheduled_arrival=f.scheduled_arrival,
                scheduled_departure=f.scheduled_departure,
                estimated_arrival=f.estimated_arrival,
                estimated_departure=f.estimated_departure,
                actual_arrival=f.actual_arrival,
                actual_departure=f.actual_departure,
                runway=f.runway,
                taxi_in_minutes=f.taxi_in_minutes,
                taxi_out_minutes=f.taxi_out_minutes,
                turnaround_minutes=f.turnaround_minutes,
                status=f.status,
                created_at=f.created_at,
                updated_at=f.updated_at,
                latest_predicted_delay=p.predicted_delay_minutes if p else 0.0,
                latest_delay_category=p.delay_category if p else "On Time",
                assigned_gate=g_num
            )
            items.append(resp_item)

        return FlightListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    @staticmethod
    def get_flight_by_id(db: Session, flight_id: int) -> Flight:
        flight = db.query(Flight).filter(Flight.id == flight_id).first()
        if not flight:
            raise FlightNotFoundError(flight_id)
        return flight

    @staticmethod
    def create_flight(db: Session, flight_in: FlightCreate) -> Flight:
        db_flight = Flight(**flight_in.model_dump())
        db.add(db_flight)
        db.commit()
        db.refresh(db_flight)
        return db_flight

    @staticmethod
    def import_csv(db: Session, file_contents: bytes) -> CSVUploadResponse:
        try:
            df = pd.read_csv(io.BytesIO(file_contents))
        except Exception as e:
            raise CSVValidationError(f"Could not parse uploaded CSV file: {str(e)}")

        required_cols = ["flight_number", "airline", "aircraft_type", "origin", "destination", "terminal", "scheduled_arrival", "scheduled_departure"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            raise CSVValidationError(f"Missing required columns in CSV: {', '.join(missing)}")

        total_rows = len(df)
        success_rows = 0
        failed_rows = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                sched_arr = pd.to_datetime(row["scheduled_arrival"]).to_pydatetime()
                sched_dep = pd.to_datetime(row["scheduled_departure"]).to_pydatetime()
                
                flight = Flight(
                    flight_number=str(row["flight_number"]).strip(),
                    airline=str(row["airline"]).strip(),
                    aircraft_type=str(row["aircraft_type"]).strip(),
                    origin=str(row["origin"]).strip(),
                    destination=str(row["destination"]).strip(),
                    terminal=str(row["terminal"]).strip(),
                    scheduled_arrival=sched_arr,
                    scheduled_departure=sched_dep,
                    runway=str(row.get("runway", "RWY-09L")),
                    taxi_in_minutes=float(row.get("taxi_in_minutes", 12.0)),
                    taxi_out_minutes=float(row.get("taxi_out_minutes", 15.0)),
                    turnaround_minutes=float(row.get("turnaround_minutes", 45.0)),
                    status=str(row.get("status", "Scheduled"))
                )
                db.add(flight)
                success_rows += 1
            except Exception as row_err:
                failed_rows += 1
                if len(errors) < 10:
                    errors.append(f"Row {idx+1}: {str(row_err)}")

        db.commit()
        return CSVUploadResponse(
            total_rows=total_rows,
            successful_rows=success_rows,
            failed_rows=failed_rows,
            errors=errors
        )
