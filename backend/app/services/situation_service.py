from app.models.situation import Situation
from app.schemas.situation import SituationCreate, SituationUpdate
from sqlalchemy.orm import Session
from app.alerts.model import Alert
from app.schemas.situation import (
    SituationContextResponse,
)
from app.situations.lifecycle import (
    validate_status_transition,
)


def create_situation(
    db: Session,
    situation_data: SituationCreate,
):
    situation = Situation(
        **situation_data.model_dump()
    )

    db.add(situation)
    db.commit()
    db.refresh(situation)

    return situation


def get_all_situations(
    db: Session,
):
    return (
        db.query(Situation)
        .order_by(Situation.created_at.desc())
        .all()
    )


def get_situation_by_id(
    db: Session,
    situation_id: int,
):
    return (
        db.query(Situation)
        .filter(Situation.id == situation_id)
        .first()
    )


def update_situation(
    db: Session,
    situation_id: int,
    situation_data: SituationUpdate,
):
    situation = get_situation_by_id(
        db,
        situation_id,
    )

    if situation is None:
        return None

    update_data = situation_data.model_dump(
        exclude_unset=True
    )

    for field, value in update_data.items():
        setattr(situation, field, value)

    db.commit()
    db.refresh(situation)

    return situation

def get_situation_context(
    db: Session,
    situation_id: int,
):
    situation = get_situation_by_id(
        db,
        situation_id,
    )

    if situation is None:
        return None

    alerts = (
        db.query(Alert)
        .filter(
            Alert.situation_id == situation_id
        )
        .order_by(Alert.created_at.asc())
        .all()
    )

    return {
        "id": situation.id,
        "title": situation.title,
        "description": situation.description,
        "severity": situation.severity,
        "status": situation.status,
        "service": situation.service,
        "environment": situation.environment,
        "created_at": situation.created_at,
        "updated_at": situation.updated_at,

        # Alert information
        "alert_count": len(alerts),

        # Correlation information
        "correlation_score": (
            situation.correlation_score
        ),
        "correlation_method": (
            situation.correlation_method
        ),
        "correlation_reasons": (
            situation.correlation_reasons
        ),

        # AI information
        "ai_summary": situation.ai_summary,
        "ai_root_cause": situation.ai_root_cause,
        "ai_recommendations": (
            situation.ai_recommendations
        ),
        "ai_status": situation.ai_status,
        "ai_updated_at": situation.ai_updated_at,

        # Related alerts
        "alerts": [
            {
                "id": alert.id,
                "title": alert.title,
                "source": alert.source,
                "severity": alert.severity,
                "service": alert.service,
                "environment": alert.environment,
                "policy_name": alert.policy_name,
                "tags": alert.tags,
            }
            for alert in alerts
        ],
    }

def update_situation_status(
    db: Session,
    situation_id: int,
    new_status: str,
):
    situation = get_situation_by_id(
        db,
        situation_id,
    )

    if situation is None:
        return None, "Situation not found"

    if not validate_status_transition(
        situation.status,
        new_status,
    ):
        return (
            None,
            (
                f"Invalid status transition: "
                f"{situation.status} → {new_status}"
            ),
        )

    situation.status = new_status

    db.commit()
    db.refresh(situation)

    return situation, None