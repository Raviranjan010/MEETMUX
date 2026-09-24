from typing import Any, Optional, Dict
from fastapi import HTTPException, status


class AppException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: str,
        details: Optional[Any] = None
    ):
        super().__init__(
            status_code=status_code,
            detail={
                "success": False,
                "error": {
                    "code": code,
                    "message": message,
                    "details": details or {}
                }
            }
        )


class FlightNotFoundError(AppException):
    def __init__(self, flight_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="FLIGHT_NOT_FOUND",
            message=f"Flight with ID {flight_id} was not found."
        )


class GateNotFoundError(AppException):
    def __init__(self, gate_id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            code="GATE_NOT_FOUND",
            message=f"Gate with ID {gate_id} was not found."
        )


class ModelNotLoadedError(AppException):
    def __init__(self, details: Optional[str] = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            code="MODEL_NOT_LOADED",
            message="Machine learning delay prediction model is not available or loaded.",
            details={"reason": details} if details else None
        )


class OptimizationInfeasibleError(AppException):
    def __init__(self, diagnostics: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            code="OPTIMIZATION_INFEASIBLE",
            message="No feasible gate assignment exists for the selected flights and gates.",
            details=diagnostics or {
                "possible_causes": [
                    "Insufficient gates available for flight count",
                    "Aircraft type incompatibility with available gates",
                    "Overlapping flight time windows at gates",
                    "Terminal restrictions or gate unavailability"
                ]
            }
        )


class OptimizationSolverError(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            code="SOLVER_ERROR",
            message=message,
            details=details
        )


class CSVValidationError(AppException):
    def __init__(self, message: str, details: Optional[Any] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            code="CSV_VALIDATION_ERROR",
            message=message,
            details=details
        )
