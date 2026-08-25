from app.auth.dependencies import get_current_user
from app.correlation.service import CorrelationService
from app.database.database import get_db
from app.models.situation import Situation
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/correlation",
    tags=["Correlation"],
)


@router.post(
    "/alerts/{alert_id}",
    response_model=dict,
)
def correlate_alert(
    alert_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = CorrelationService()

    situation = service.correlate_alert(
        db,
        alert_id,
    )

    if situation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No related alerts found",
        )

    return {
        "message": "Alert correlation completed",
        "situation_id": situation.id,
        "title": situation.title,
        "severity": situation.severity,
        "status": situation.status,
    }