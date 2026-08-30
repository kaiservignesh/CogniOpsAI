from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class WorkflowExecutionResponse(BaseModel):
    id: int
    situation_id: int
    policy_id: int
    status: str
    action_type: str | None = None
    action_target: str | None = None
    action_payload: dict[str, Any] | None = None
    result: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )