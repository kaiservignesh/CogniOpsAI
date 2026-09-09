from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.alerts.model import Alert
from app.alerts.schema import AlertCreate, AlertUpdate
from app.correlation.service import CorrelationService


# Reuse one correlation service instance
correlation_service = CorrelationService()


def create_alert(db: Session, alert: AlertCreate):
    db_alert = Alert(**alert.model_dump())

    db.add(db_alert)
    db.commit()
    db.refresh(db_alert)

    # Automatically correlate the newly created alert.
    # A failure in correlation should not prevent the alert
    # itself from being successfully created.
    try:
        correlation_service.correlate_alert(
            db=db,
            alert_id=db_alert.id,
        )
    except Exception as exc:
        print(
            f"Automatic correlation failed for alert "
            f"{db_alert.id}: {type(exc).__name__}: {exc}"
        )

    # Refresh again because correlation may have assigned
    # a situation_id to the alert.
    db.refresh(db_alert)

    return db_alert


def get_all_alerts(db: Session):
    return db.query(Alert).all()


def get_alert_by_id(db: Session, alert_id: int):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()

    if alert is None:
        raise HTTPException(
            status_code=404,
            detail="Alert not found",
        )

    return alert


def update_alert(
    db: Session,
    alert_id: int,
    alert_data: AlertUpdate,
):
    alert = get_alert_by_id(db, alert_id)

    update_data = alert_data.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(alert, key, value)

    db.commit()
    db.refresh(alert)

    return alert


def delete_alert(
    db: Session,
    alert_id: int,
):
    alert = get_alert_by_id(db, alert_id)

    db.delete(alert)
    db.commit()

    return {
        "message": "Alert deleted successfully"
    }