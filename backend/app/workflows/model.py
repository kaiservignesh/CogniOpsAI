from datetime import datetime, timezone

from app.database.database import Base
from sqlalchemy import Boolean, Column, DateTime, Integer, JSON, String, Text


class WorkflowPolicy(Base):
    __tablename__ = "workflow_policies"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(
        String(255),
        nullable=False,
        unique=True,
    )

    description = Column(
        Text,
        nullable=True,
    )

    enabled = Column(
        Boolean,
        nullable=False,
        default=True,
    )

    condition = Column(
        JSON,
        nullable=False,
    )

    action = Column(
        JSON,
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )