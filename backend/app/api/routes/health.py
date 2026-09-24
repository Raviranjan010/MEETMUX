import logging
from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel
from app.core.db import check_db_health
from app.ml.registry import registry

router = APIRouter(tags=["Health"])
logger = logging.getLogger(__name__)


def check_gurobi() -> bool:
    try:
        import gurobipy as gp
        # Quick license/model check
        m = gp.Model("test_health")
        m.dispose()
        return True
    except Exception:
        return False


def check_ortools() -> bool:
    try:
        from ortools.sat.python import cp_model
        model = cp_model.CpModel()
        return True
    except Exception:
        return False


class OptimizerHealth(BaseModel):
    gurobi_available: bool
    ortools_available: bool


class HealthResponse(BaseModel):
    status: str
    database: bool
    ml_model_loaded: bool
    optimizer: OptimizerHealth


@router.get("/health", response_model=HealthResponse)
def get_health() -> Dict[str, Any]:
    db_ok = check_db_health()
    ml_ok = registry.is_loaded()
    gurobi_ok = check_gurobi()
    ortools_ok = check_ortools()

    # Per API.md: status is degraded if database is false OR both solvers unavailable
    if not db_ok or (not gurobi_ok and not ortools_ok):
        overall_status = "degraded"
    else:
        overall_status = "ok"

    return {
        "status": overall_status,
        "database": db_ok,
        "ml_model_loaded": ml_ok,
        "optimizer": {
            "gurobi_available": gurobi_ok,
            "ortools_available": ortools_ok,
        },
    }
