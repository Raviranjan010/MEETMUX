import json
from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.models.flight import Flight
from app.models.gate import Gate
from app.models.prediction import DelayPrediction
from app.models.optimization import OptimizationRun, GateAssignment
from app.schemas.optimization import (
    OptimizationRequest,
    OptimizationResponse,
    OptimizationRunSummary,
    GateAssignmentItem,
    OptimizationDiagnostics,
    OptimizationWeights as SchemaOptWeights
)
from app.optimization.models import (
    FlightOptInput,
    GateOptInput,
    OptWeights,
    OptimizationOutput
)
from app.optimization.optimizer import OptimizerFactory, OptimizationValidator
from app.core.exceptions import AppException
from app.core.logging import logger


class OptimizationService:
    @staticmethod
    def run_optimization(db: Session, request: OptimizationRequest) -> OptimizationResponse:
        logger.info(f"Received optimization request with solver='{request.solver}'")

        # 1. Fetch Flights
        flight_query = db.query(Flight)
        if request.flight_ids:
            flight_query = flight_query.filter(Flight.id.in_(request.flight_ids))
        flights_db = flight_query.all()

        # 2. Fetch Gates
        gate_query = db.query(Gate)
        if request.gate_ids:
            gate_query = gate_query.filter(Gate.id.in_(request.gate_ids))
        gates_db = gate_query.all()

        if not flights_db:
            raise AppException(status_code=400, code="NO_FLIGHTS", message="No flights selected for optimization.")
        if not gates_db:
            raise AppException(status_code=400, code="NO_GATES", message="No gates available for optimization.")

        # 3. Fetch latest predicted delays for these flights
        flight_ids = [f.id for f in flights_db]
        preds = (
            db.query(DelayPrediction)
            .filter(DelayPrediction.flight_id.in_(flight_ids))
            .order_by(desc(DelayPrediction.prediction_timestamp))
            .all()
        )
        pred_map = {}
        for p in preds:
            if p.flight_id not in pred_map:
                pred_map[p.flight_id] = p

        # 4. Prepare Optimization Inputs
        flight_inputs = []
        for f in flights_db:
            p = pred_map.get(f.id)
            pred_delay = p.predicted_delay_minutes if p else (f.taxi_in_minutes or 0.0)
            delay_cat = p.delay_category if p else "On Time"

            flight_inputs.append(FlightOptInput(
                id=f.id,
                flight_number=f.flight_number,
                airline=f.airline,
                aircraft_type=f.aircraft_type,
                terminal=f.terminal,
                arrival_time=f.scheduled_arrival,
                departure_time=f.scheduled_departure,
                turnaround_minutes=f.turnaround_minutes or 45.0,
                predicted_delay_minutes=pred_delay,
                delay_category=delay_cat
            ))

        gate_inputs = [
            GateOptInput(
                id=g.id,
                gate_number=g.gate_number,
                terminal=g.terminal,
                gate_type=g.gate_type or "Contact",
                supported_aircraft_types=g.supported_aircraft_types or "*",
                is_international=bool(g.is_international),
                is_available=bool(g.is_available)
            )
            for g in gates_db
        ]

        # Weights
        w_req = request.weights or SchemaOptWeights()
        weights = OptWeights(
            conflict=w_req.conflict,
            walking_distance=w_req.walking_distance,
            delay_propagation=w_req.delay_propagation,
            reassignment=w_req.reassignment,
            unused_gate=w_req.unused_gate
        )

        # 5. Execute Solver
        optimizer = OptimizerFactory.get_optimizer(request.solver or "ortools")
        opt_output: OptimizationOutput = optimizer.solve(
            flights=flight_inputs,
            gates=gate_inputs,
            weights=weights,
            time_limit_seconds=request.time_limit_seconds or 60,
            buffer_minutes=request.buffer_minutes or 15.0
        )

        # 6. Validate Solver Results
        flights_map = {f.id: f for f in flight_inputs}
        gates_map = {g.id: g for g in gate_inputs}
        is_valid, validation_errors, warnings = OptimizationValidator.validate_assignments(
            assignments=opt_output.assignments,
            flights_map=flights_map,
            gates_map=gates_map,
            buffer_minutes=request.buffer_minutes or 15.0
        )

        # 7. Persist Optimization Run & Assignments to DB
        db_run = OptimizationRun(
            status=opt_output.status,
            solver=opt_output.solver,
            objective_value=opt_output.objective_value,
            execution_time=opt_output.execution_time_seconds,
            total_flights=opt_output.total_flights,
            total_gates=opt_output.total_gates,
            assigned_flights=opt_output.assigned_flights,
            unassigned_flights=opt_output.unassigned_flights,
            gates_utilized=opt_output.gates_utilized,
            conflicts_count=len(validation_errors),
            metrics_summary=json.dumps({
                "gates_utilized": opt_output.gates_utilized,
                "warnings": warnings,
                "errors": validation_errors
            }),
            created_at=datetime.utcnow()
        )
        db.add(db_run)
        db.flush()

        # Save Gate Assignments
        saved_assignments = []
        for a in opt_output.assignments:
            db_assign = GateAssignment(
                flight_id=a.flight_id,
                gate_id=a.gate_id,
                optimization_run_id=db_run.id,
                arrival_time=a.arrival_time,
                departure_time=a.departure_time,
                assignment_status=a.assignment_status,
                passenger_walk_score=a.walking_distance_score
            )
            db.add(db_assign)
            
            saved_assignments.append(GateAssignmentItem(
                flight_id=a.flight_id,
                flight_number=a.flight_number,
                airline=a.airline,
                aircraft_type=a.aircraft_type,
                terminal=a.terminal,
                gate_id=a.gate_id,
                gate_number=a.gate_number,
                gate_terminal=a.gate_terminal,
                arrival_time=a.arrival_time,
                departure_time=a.departure_time,
                predicted_delay_minutes=a.predicted_delay_minutes,
                delay_category=a.delay_category,
                assignment_status=a.assignment_status,
                walking_distance_score=a.walking_distance_score
            ))

        db.commit()
        db.refresh(db_run)

        return OptimizationResponse(
            optimization_run_id=db_run.id,
            status=opt_output.status.lower(),
            solver=opt_output.solver,
            objective_value=opt_output.objective_value,
            execution_time_seconds=opt_output.execution_time_seconds,
            total_flights=opt_output.total_flights,
            total_gates=opt_output.total_gates,
            assigned_flights=opt_output.assigned_flights,
            unassigned_flights=opt_output.unassigned_flights,
            gates_utilized=opt_output.gates_utilized,
            conflicts=len(validation_errors),
            assignments=saved_assignments,
            diagnostics=OptimizationDiagnostics(
                is_valid=is_valid,
                errors=validation_errors,
                warnings=warnings,
                conflict_count=len(validation_errors)
            ),
            message=opt_output.message
        )

    @staticmethod
    def get_run_by_id(db: Session, run_id: int) -> OptimizationRunSummary:
        run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        if not run:
            raise AppException(status_code=404, code="RUN_NOT_FOUND", message=f"Optimization run #{run_id} not found.")
        return OptimizationRunSummary.model_validate(run)

    @staticmethod
    def get_run_assignments(db: Session, run_id: int) -> List[GateAssignmentItem]:
        run = db.query(OptimizationRun).filter(OptimizationRun.id == run_id).first()
        if not run:
            raise AppException(status_code=404, code="RUN_NOT_FOUND", message=f"Optimization run #{run_id} not found.")

        assignments = db.query(GateAssignment).filter(GateAssignment.optimization_run_id == run_id).all()
        results = []
        for a in assignments:
            results.append(GateAssignmentItem(
                flight_id=a.flight_id,
                flight_number=a.flight.flight_number if a.flight else "",
                airline=a.flight.airline if a.flight else "",
                aircraft_type=a.flight.aircraft_type if a.flight else "",
                terminal=a.flight.terminal if a.flight else "",
                gate_id=a.gate_id,
                gate_number=a.gate.gate_number if a.gate else "",
                gate_terminal=a.gate.terminal if a.gate else "",
                arrival_time=a.arrival_time,
                departure_time=a.departure_time,
                predicted_delay_minutes=0.0,
                delay_category="On Time",
                assignment_status=a.assignment_status,
                walking_distance_score=a.passenger_walk_score
            ))
        return results
