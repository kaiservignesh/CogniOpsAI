from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SituationBase(BaseModel):
    title: str
    description: str | None = None
    severity: str = "Medium"
    status: str = "Open"
    service: str | None = None
    environment: str | None = None


class SituationCreate(SituationBase):
    pass


class SituationUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    severity: str | None = None
    status: str | None = None
    service: str | None = None
    environment: str | None = None


class SituationResponse(SituationBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)