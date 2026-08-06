from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class AlertCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source: str
    severity: str
    policy_name: Optional[str] = None
    tags: Optional[str] = None
    service: Optional[str] = None
    environment: Optional[str] = None


class AlertUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    severity: Optional[str] = None
    status: Optional[str] = None
    policy_name: Optional[str] = None
    tags: Optional[str] = None
    service: Optional[str] = None
    environment: Optional[str] = None


class AlertResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    source: str
    severity: str
    status: str
    policy_name: Optional[str]
    tags: Optional[str]
    service: Optional[str]
    environment: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {
        "from_attributes": True
    }