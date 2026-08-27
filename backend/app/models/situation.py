from datetime import datetime, timezone

from app.database.database import Base
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import relationship

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    Integer,
    JSON,
    String,
    Text,
)


class Situation(Base):
    __tablename__ = "situations"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)

    description = Column(Text, nullable=True)

    severity = Column(
        String(50),
        nullable=False,
        default="Medium",
    )

    status = Column(
        String(50),
        nullable=False,
        default="Open",
    )

    service = Column(
        String(255),
        nullable=True,
    )

    environment = Column(
        String(100),
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

    alerts = relationship(
        "Alert",
        back_populates="situation",
    )

    correlation_score = Column(
        Float,
        nullable=True,
    )

    correlation_method = Column(
        String(100),
        nullable=True,
    )

    correlation_reasons = Column(
        JSON,
        nullable=True,
    )