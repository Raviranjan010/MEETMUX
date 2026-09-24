from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.services.dashboard_service import DashboardService
from app.schemas.dashboard import DashboardSummaryResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse, summary="Get Complete Airport Operations Dashboard Summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    return DashboardService.get_dashboard_summary(db)
