from datetime import datetime, timezone

from app.database.database import Base
from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    JSON,
    String,
    Text,
)


class WorkflowExecution(Base):
    __tablename__ = "workflow_executions"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
    )

    situation_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    policy_id = Column(
        Integer,
        nullable=False,
        index=True,
    )

    status = Column(
        String(50),
        nullable=False,
        default="Pending",
    )

    action_type = Column(
        String(100),
        nullable=True,
    )

    action_target = Column(
        String(255),
        nullable=True,
    )

    action_payload = Column(
        JSON,
        nullable=True,
    )

    result = Column(
        Text,
        nullable=True,
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