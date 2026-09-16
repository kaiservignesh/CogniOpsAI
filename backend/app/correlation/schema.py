from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CorrelationPolicyBase(BaseModel):
    name: str
    description: str | None = None
    enabled: bool = True
    condition: dict[str, Any]
    time_window_minutes: int = Field(default=5, ge=1, le=1440)


class CorrelationPolicyCreate(CorrelationPolicyBase):
    pass


class CorrelationPolicyUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    enabled: bool | None = None
    condition: dict[str, Any] | None = None
    time_window_minutes: int | None = Field(default=None, ge=1, le=1440)


class CorrelationPolicyResponse(CorrelationPolicyBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
