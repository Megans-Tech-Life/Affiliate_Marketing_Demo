from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timezone
from apps.auth.security import get_current_admin
from .dashboard_schemas import DashboardResponse, DashboardMetric
from .dashboard_services import get_all_metrics, apply_date_filters
from core.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Admin Dashboard"])

# Admin dashboard route to get metrics
@router.get("/", response_model=DashboardResponse)
def get_admin_dashboard(
    start_date:Optional[str] = Query(None),
    end_date:Optional[str] = Query(None),
    db: Session = Depends(get_db),
    admin_user: dict = Depends(get_current_admin)
):
    start_date_obj = None
    end_date_obj = None

    # Parse and convert start_date to UTC
    if start_date:
        try:
            start_date_obj = datetime.fromisoformat(start_date)
            if start_date_obj.tzinfo is None:
                start_date_obj = start_date_obj.replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(400, "Invalid start_date format. Use ISO format: YYYY-MM-DD")

    # Parse and convert end_date to UTC
    if end_date:
        try:
            end_date_obj = datetime.fromisoformat(end_date)
            if end_date_obj.tzinfo is None:
                end_date_obj = end_date_obj.replace(tzinfo=timezone.utc)
        except ValueError:
            raise HTTPException(400, "Invalid end_date format. Use ISO format: YYYY-MM-DD")

    metrics = get_all_metrics(db, start_date_obj, end_date_obj)
    metrics_list = [
        DashboardMetric(name=key, total=value) for key, value in metrics.items()
    ]
    return DashboardResponse(metrics=metrics_list)