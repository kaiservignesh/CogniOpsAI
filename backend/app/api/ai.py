from app.ai.service import AIService
from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.services.situation_service import get_situation_context
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


@router.post("/situations/{situation_id}/summary")
def generate_situation_summary(
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

    service = AIService()

    summary = service.summarize_situation(
        context
    )

    return {
        "situation_id": situation_id,
        "summary": summary,
    }

@router.post(
    "/situations/{situation_id}/root-cause"
)
def analyze_root_cause(
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

    service = AIService()

    analysis = service.analyze_root_cause(
        context
    )

    return {
        "situation_id": situation_id,
        "root_cause_analysis": analysis,
    }

@router.post(
    "/situations/{situation_id}/recommendations"
)
def recommend_actions(
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

    service = AIService()

    recommendations = service.recommend_actions(
        context
    )

    return {
        "situation_id": situation_id,
        "recommendations": recommendations,
    }

@router.post(
    "/situations/{situation_id}/store-context"
)
def store_situation_context(
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

    service = AIService()

    return service.store_situation(
        context
    )