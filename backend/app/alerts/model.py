from datetime import datetime
from app.models.situation import Situation

from app.database.database import Base
from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    source = Column(String(100), nullable=False)

    severity = Column(String(50), nullable=False)

    status = Column(
        String(50),
        nullable=False,
        default="Open",
    )

    policy_name = Column(String(255), nullable=True)

    tags = Column(String(500), nullable=True)

    service = Column(
        String(255),
        nullable=True,
    )

    environment = Column(
        String(100),
        nullable=True,
    )

    situation_id = Column(
        Integer,
        ForeignKey("situations.id"),
        nullable=True,
    )

    situation = relationship(
        "Situation",
        back_populates="alerts",
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow,
    )

    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )