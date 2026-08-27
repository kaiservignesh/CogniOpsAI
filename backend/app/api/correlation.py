from app.auth.dependencies import get_current_user
from app.correlation.service import CorrelationService
from app.database.database import get_db
from app.models.situation import Situation
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.alerts.model import Alert


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

    result = service.correlate_alert(
        db,
        alert_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No related alerts or situations found",
        )

    situation = result["situation"]

    return {
        "message": "Alert correlation completed",
        "situation_id": situation.id,
        "title": situation.title,
        "severity": situation.severity,
        "status": situation.status,
        "correlation_score": result["score"],
        "correlation_reasons": result["reasons"],
        "ai_status": situation.ai_status,
    }

@router.post(
    "/alerts/{alert_id}/analyze"
)
def analyze_alert_correlation(
    alert_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    alert = (
        db.query(Alert)
        .filter(Alert.id == alert_id)
        .first()
    )

    if alert is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )

    service = CorrelationService()

    result = service.hybrid_correlation_analysis(
        db,
        alert,
    )

    return {
        "alert_id": alert_id,
        **result,
    }