from app.auth.dependencies import get_current_user
from app.correlation.policy_service import CorrelationPolicyService
from app.correlation.schema import (
    CorrelationPolicyCreate,
    CorrelationPolicyResponse,
    CorrelationPolicyUpdate,
)
from app.database.database import get_db
from app.models.user import User
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


router = APIRouter(
    prefix="/correlation/policies",
    tags=["Correlation Policies"],
)


@router.post(
    "/",
    response_model=CorrelationPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_policy(
    policy: CorrelationPolicyCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return CorrelationPolicyService().create_policy(db, policy)


@router.get(
    "/",
    response_model=list[CorrelationPolicyResponse],
)
def get_policies(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return CorrelationPolicyService().get_all_policies(db)


@router.get(
    "/{policy_id}",
    response_model=CorrelationPolicyResponse,
)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    policy = CorrelationPolicyService().get_policy_by_id(db, policy_id)
    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correlation policy not found",
        )
    return policy


@router.put(
    "/{policy_id}",
    response_model=CorrelationPolicyResponse,
)
def update_policy(
    policy_id: int,
    policy: CorrelationPolicyUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    updated = CorrelationPolicyService().update_policy(
        db,
        policy_id,
        policy,
    )
    if updated is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Correlation policy not found",
        )
    return updated
