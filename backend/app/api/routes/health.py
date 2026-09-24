from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.api.dependencies import get_db
from app.ml.model_registry import model_registry
from app.optimization.gurobi_solver import GUROBI_AVAILABLE

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", summary="System Health Status Check")
def health_check(db: Session = Depends(get_db)):
    # Check DB
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    # Check Model
    model_status = "loaded" if model_registry.is_loaded() else "unavailable"

    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "database": db_status,
        "model": model_status,
        "optimizer": "available",
        "solvers": {
            "ortools": "available",
            "gurobi": "available" if GUROBI_AVAILABLE else "fallback_to_ortools"
        }
    }
