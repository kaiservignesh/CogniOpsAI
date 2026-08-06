from app.models.situation import Situation
from app.schemas.situation import SituationCreate, SituationUpdate
from sqlalchemy.orm import Session


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