from app.auth.dependencies import get_current_user
from app.database.database import get_db
from app.models.user import User
from app.workflows.schema import (
    WorkflowPolicyCreate,
    WorkflowPolicyResponse,
    WorkflowPolicyUpdate,
)
from app.workflows.execution_schema import (
    WorkflowExecutionResponse,
)
from app.workflows.service import WorkflowPolicyService
from app.workflows.execution import WorkflowExecution
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.workflows.execution import WorkflowExecution


router = APIRouter(
    prefix="/workflows/policies",
    tags=["Workflow Policies"],
)


@router.post(
    "/",
    response_model=WorkflowPolicyResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_policy(
    policy: WorkflowPolicyCreate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = WorkflowPolicyService()

    return service.create_policy(
        db,
        policy,
    )


@router.get(
    "/",
    response_model=list[WorkflowPolicyResponse],
)
def get_policies(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = WorkflowPolicyService()

    return service.get_all_policies(db)


@router.get(
    "/{policy_id}",
    response_model=WorkflowPolicyResponse,
)
def get_policy(
    policy_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = WorkflowPolicyService()

    policy = service.get_policy_by_id(
        db,
        policy_id,
    )

    if policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow policy not found",
        )

    return policy


@router.put(
    "/{policy_id}",
    response_model=WorkflowPolicyResponse,
)
def update_policy(
    policy_id: int,
    policy: WorkflowPolicyUpdate,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = WorkflowPolicyService()

    updated_policy = service.update_policy(
        db,
        policy_id,
        policy,
    )

    if updated_policy is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow policy not found",
        )

    return updated_policy

@router.get(
    "/executions/",
    response_model=list[
        WorkflowExecutionResponse
    ],
)
def get_executions(
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    return (
        db.query(WorkflowExecution)
        .order_by(
            WorkflowExecution.created_at.desc()
        )
        .all()
    )

@router.post(
    "/executions/{execution_id}/run",
    response_model=WorkflowExecutionResponse,
)
def run_execution(
    execution_id: int,
    db: Session = Depends(get_db),  # noqa: B008
    current_user: User = Depends(get_current_user),  # noqa: B008
):
    service = WorkflowPolicyService()

    execution = service.execute_workflow(
        db,
        execution_id,
    )

    if execution is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workflow execution not found",
        )

    return execution