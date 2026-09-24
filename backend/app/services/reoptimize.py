"""
Re-optimization orchestrator per docs/REOPTIMIZATION.md.
FR-12: Re-run pipeline post-scenario.
"""
import logging
from typing import Dict, Any, Optional

from sqlalchemy.orm import Session

from app.models import (
    Flight, Scenario, OptimizationRun, SystemConfig, Prediction,
    WeatherRecord,
)
from app.models.enums import OptimizationStatus, AuditAction
from app.models import AuditRecord
from app.ml.predict import predict_for_flight
from app.services.conflict import detect_conflicts_from_db
from app.services.cascade import analyze_cascade
from app.optimizer.milp import run_milp_optimization
from app.services.alerts import generate_alerts_from_state

logger = logging.getLogger(__name__)


def reoptimize_after_scenario(
    db: Session,
    scenario_id: str,
) -> Dict[str, Any]:
    """
    Full re-optimization pipeline per REOPTIMIZATION.md:
    1. Identify affected flights
    2. Re-predict for affected flights
    3. Re-detect conflicts
    4. Cascade analysis
    5. MILP optimization
    6. Independent validation
    7. Persist new run
    8. Update alerts
    """
    scenario = db.query(Scenario).filter(Scenario.id == scenario_id).first()
    if not scenario:
        return {"error": "Scenario not found"}
    
    config = db.query(SystemConfig).first()
    result = {"steps": [], "scenario_id": scenario_id}
    
    try:
        # Step 1: Identify affected flights
        affected_flights = db.query(Flight).all()  # Re-predict all for simplicity
        result["steps"].append({
            "step": 1,
            "name": "identify_affected",
            "flights_count": len(affected_flights),
        })
        
        # Step 2: Re-run predictions for affected flights
        prediction_count = 0
        latest_weather = db.query(WeatherRecord).order_by(
            WeatherRecord.recorded_at.desc()
        ).first()
        
        for flight in affected_flights:
            try:
                predict_for_flight(flight, db, weather=latest_weather, config=config, persist=True)
                prediction_count += 1
            except Exception as e:
                logger.warning(f"Prediction failed for {flight.flight_number}: {e}")
        
        result["steps"].append({
            "step": 2,
            "name": "re_predict",
            "predictions_updated": prediction_count,
        })
        
        # Step 3: Detect conflicts
        conflicts = detect_conflicts_from_db(db, assignment_source="BASELINE")
        result["steps"].append({
            "step": 3,
            "name": "conflict_detection",
            "conflicts_found": len(conflicts),
        })
        
        # Step 4: Cascade analysis
        cascade_result = None
        if scenario.type.value in ("RUNWAY_CLOSURE", "GATE_CLOSURE"):
            # Find root entity
            from app.models import Runway, Gate
            if scenario.type.value == "RUNWAY_CLOSURE":
                rwy = db.query(Runway).filter(Runway.code == scenario.target_reference).first()
                if rwy:
                    cascade_result = analyze_cascade(
                        db, root_runway_id=str(rwy.id), scenario_id=scenario_id
                    )
            elif scenario.type.value == "GATE_CLOSURE":
                gate = db.query(Gate).filter(Gate.code == scenario.target_reference).first()
                if gate:
                    cascade_result = analyze_cascade(
                        db, root_gate_id=str(gate.id), scenario_id=scenario_id
                    )
        elif scenario.type.value in ("FLIGHT_DELAY", "CASCADE_DELAY"):
            flight = db.query(Flight).filter(
                Flight.flight_number == scenario.target_reference
            ).first()
            if flight:
                cascade_result = analyze_cascade(
                    db, root_flight_id=str(flight.id), scenario_id=scenario_id
                )
        
        result["steps"].append({
            "step": 4,
            "name": "cascade_analysis",
            "cascade": cascade_result,
        })
        
        # Step 5 & 6: MILP optimization + validation
        opt_result = run_milp_optimization(db, scenario_id=scenario_id)
        
        result["steps"].append({
            "step": 5,
            "name": "milp_optimization",
            "optimization_run_id": opt_result.get("optimization_run_id"),
            "status": opt_result.get("status"),
            "solver_used": opt_result.get("solver_used"),
            "objective_value": opt_result.get("objective_value"),
            "validation_passed": opt_result.get("validation_passed"),
        })
        
        # Step 7: Link scenario to new optimization run
        if "optimization_run_id" in opt_result:
            scenario.resulting_optimization_run_id = opt_result["optimization_run_id"]
        
        # Step 8: Update alerts
        new_alerts = generate_alerts_from_state(db)
        result["steps"].append({
            "step": 8,
            "name": "alert_update",
            "new_alerts": len(new_alerts),
        })
        
        db.commit()
        
        result["optimization_run_id"] = opt_result.get("optimization_run_id")
        result["status"] = opt_result.get("status", "COMPLETED")
        result["solver_used"] = opt_result.get("solver_used")
        
    except Exception as e:
        logger.error(f"Re-optimization failed: {e}")
        result["status"] = "ERROR"
        result["error"] = str(e)
    
    return result
