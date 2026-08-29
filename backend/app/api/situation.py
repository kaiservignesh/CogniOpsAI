from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.schemas.situation import (
    SituationContextResponse,
    SituationCreate,
    SituationResponse,
    SituationUpdate,
)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.situation import (
    SituationContextResponse,
)
from app.services.situation_service import (
    create_situation,
    get_all_situations,
    get_situation_by_id,
    get_situation_context,
    update_situation,
)
from app.schemas.situation import (
    SituationStatusUpdate,
)
from app.services.situation_service import (
    update_situation_status,
)

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

@router.get(
    "/{situation_id}/context",
    response_model=SituationContextResponse,
)
def get_situation_context_api(
    situation_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    context = get_situation_context(
        db,
        situation_id,
    )

    if context is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Situation not found",
        )

    return context

@router.patch(
    "/{situation_id}/status",
    response_model=SituationResponse,
)
def change_situation_status(
    situation_id: int,
    status_update: SituationStatusUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    situation, error = update_situation_status(
        db,
        situation_id,
        status_update.status,
    )

    if situation is None:
        if error == "Situation not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=error,
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error,
        )

    return situation