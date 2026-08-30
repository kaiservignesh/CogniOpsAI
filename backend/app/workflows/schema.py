from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class WorkflowPolicyBase(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True
    condition: dict[str, Any]
    action: dict[str, Any]


class WorkflowPolicyCreate(WorkflowPolicyBase):
    pass


class WorkflowPolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    condition: dict[str, Any] | None = None
    action: dict[str, Any] | None = None


class WorkflowPolicyResponse(WorkflowPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )