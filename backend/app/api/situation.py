from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.situation import (
    SituationCreate,
    SituationResponse,
    SituationUpdate,
)
from app.services.situation_service import (
    create_situation,
    get_all_situations,
    get_situation_by_id,
    update_situation,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/situations",
    tags=["Situations"],
)


@router.post(
    "/",
    response_model=SituationResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_situation(
    situation: SituationCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return create_situation(db, situation)


@router.get(
    "/",
    response_model=list[SituationResponse],
)
def get_situations(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return get_all_situations(db)


@router.get(
    "/{situation_id}",
    response_model=SituationResponse,
)
def get_situation(
    situation_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    situation = get_situation_by_id(
        db,
        situation_id,
    )

    if situation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Situation not found",
        )

    return situation


@router.put(
    "/{situation_id}",
    response_model=SituationResponse,
)
def edit_situation(
    situation_id: int,
    situation: SituationUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    updated_situation = update_situation(
        db,
        situation_id,
        situation,
    )

    if updated_situation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Situation not found",
        )

    return updated_situation